from langchain_core.tools import Tool


def retrieve_with_sources(retriever, question):
    documents = retriever.invoke(question)

    if not documents:
        return "No relevant documents were found."

    results = []

    for document in documents:
        source = document.metadata.get("source", "Unknown source")
        page = document.metadata.get("page")

        if page is not None:
            location = f"{source}, page {page + 1}"
        else:
            location = source

        results.append(
            f"Source: {location}\n"
            f"Content:\n{document.page_content}"
        )

    return "\n\n---\n\n".join(results)



def create_retrieval_tool(retriever):
    return Tool(
        name="api_standards_db",
        func=lambda question: retrieve_with_sources(retriever, question),
        description=(
            "Use this tool for questions about API standards, inspection," \
        "corrosion, piping, tanks, and related engineering requirements. " \
        "The tool returns relevant source content with document and page metadata."
        ),
    )