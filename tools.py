from langchain_core.tools import Tool
from urllib.parse import quote


def build_document_url(source_path: str, page: int | None) -> str:
    filename = source_path.replace("\\", "/").split("/")[-1]
    encoded_filename = quote(filename)
    url = f"/documents/{encoded_filename}"

    if page is not None:
        url += f"#page={page}"

    return url



def retrieve_with_sources(retriever, question):
    documents = retriever.invoke(question)

    if not documents:
        return []

    results = []

    for document in documents:
        source = document.metadata.get("source", "Unknown source")
        page = document.metadata.get("page")
        page_number = page + 1 if page is not None else None

        results.append({
            "source": source,
            "page": page_number,
            "url": build_document_url(source, page_number),
            "snippet": document.page_content[:400],
        })

    return results



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