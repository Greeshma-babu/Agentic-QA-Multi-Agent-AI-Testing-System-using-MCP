print("Starting Qwen connection test...")

try:
    from langchain_ollama import ChatOllama

    print("LangChain Ollama imported successfully.")

    llm = ChatOllama(model="qwen2.5:0.5b", temperature=0)

    print("Sending request to Qwen...")

    response = llm.invoke("Reply with: Qwen connection successful")

    print("\nQWEN RESPONSE:")
    print(response.content)

except Exception as e:
    print("\nERROR OCCURRED:")
    print(repr(e))
