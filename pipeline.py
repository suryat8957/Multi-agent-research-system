from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

def run_research_pipeline(topic: str, step_callback=None) -> dict:
    """
    Executes the multi-agent research pipeline:
      1. Search Agent: Queries Tavily web search
      2. Reader Agent: Deep-scrapes top resource
      3. Writer Chain: Synthesizes gathered knowledge into a comprehensive report
      4. Critic Chain: Evaluates and scores the final report
    """
    state = {}

    def _notify(step: int, name: str, status: str, content=None):
        if step_callback and callable(step_callback):
            step_callback(step, name, status, content)

    # Step 1: Search Agent
    print("\n" + "=" * 50)
    print("Step 1 - Search agent is working...")
    print("=" * 50)
    _notify(1, "Search Agent", "Searching the web for reliable sources...", None)

    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })
    
    last_search_msg = search_result['messages'][-1].content
    state["search_results"] = (
        "\n".join([str(item) for item in last_search_msg])
        if isinstance(last_search_msg, list)
        else str(last_search_msg)
    )

    print("\nSearch result:\n", state['search_results'])
    _notify(1, "Search Agent", "Search completed", state["search_results"])

    # Step 2: Reader Agent
    print("\n" + "=" * 50)
    print("Step 2 - Reader agent is scraping top resources...")
    print("=" * 50)
    _notify(2, "Reader Agent", "Scraping deep content from primary sources...", None)

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:800]}"
        )]
    })

    last_reader_msg = reader_result['messages'][-1].content
    state['scraped_content'] = (
        "\n".join([str(item) for item in last_reader_msg])
        if isinstance(last_reader_msg, list)
        else str(last_reader_msg)
    )

    print("\nScraped content:\n", state['scraped_content'])
    _notify(2, "Reader Agent", "Scraping completed", state["scraped_content"])

    # Step 3: Writer Chain
    print("\n" + "=" * 50)
    print("Step 3 - Writer is drafting the report...")
    print("=" * 50)
    _notify(3, "Writer Agent", "Synthesizing research and drafting report...", None)

    research_combined = (
        f"SEARCH RESULTS:\n{state['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })

    print("\nFinal Report:\n", state['report'])
    _notify(3, "Writer Agent", "Drafting completed", state["report"])

    # Step 4: Critic Chain
    print("\n" + "=" * 50)
    print("Step 4 - Critic is reviewing the report...")
    print("=" * 50)
    _notify(4, "Critic Agent", "Reviewing report quality and generating evaluation...", None)

    state["feedback"] = critic_chain.invoke({
        "report": state['report']
    })

    print("\nCritic report:\n", state['feedback'])
    _notify(4, "Critic Agent", "Evaluation completed", state["feedback"])

    return state


if __name__ == "__main__":
    topic = input("\nEnter a research topic: ")
    run_research_pipeline(topic)
