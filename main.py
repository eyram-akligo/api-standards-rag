from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain.agents import create_agent
from config import MODEL_NAME
from database import get_retriever
from tools import create_retrieval_tool


def main():
    llm = ChatNVIDIA(model=MODEL_NAME)
    retriever = get_retriever()
    tool = create_retrieval_tool(retriever)
    agent = create_agent(llm, tools=[tool])

    print("API Standards RAG Agent")
    print("Type 'quit' to exit.")

    while True:
        question = input("\nQuestion: ").strip()

        if question.lower() in {"quit", "exit", "q"}:
            break

        if not question:
            continue

        response = agent.invoke({
            "messages": [("user", question)]
        })

        print("\nAnswer:")
        print(response["messages"][-1].content)

if __name__ == "__main__":
    main()