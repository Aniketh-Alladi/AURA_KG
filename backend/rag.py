import os
from typing import Dict, Any
from openai import OpenAI
from backend.retriever import retrieve_context

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def build_system_prompt() -> str:
    """
    Constructs the system prompt that constrains the LLM to answer 
    STRICTLY based on the retrieved knowledge graph context.
    """
    return (
        "You are an expert AI assistant for AURA-KG, a personal knowledge management system. "
        "Answer the user's question accurately and concisely using ONLY the provided Knowledge Graph context.\n\n"
        "Guidelines:\n"
        "1. Do not assume or extrapolate information beyond what is explicitly stated in the context.\n"
        "2. If the context does not contain enough information to answer the query, clearly state that you don't know based on the current graph data.\n"
        "3. Keep your explanation direct and easy to read."
    )


def synthesize_answer(query: str, text_context: str) -> str:
    """
    Calls the LLM API to generate a natural language response based on retrieved context.
    """
    system_prompt = build_system_prompt()
    
    user_prompt = f"""
Context from Knowledge Graph:
-----------------------------
{text_context}

-----------------------------
User Question: {query}
Answer:
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    
    # Extract and return the output text string
    return response.choices[0].message.content.strip()


def answer_query(query: str, top_k: int = 3) -> Dict[str, Any]:
    """
    Full End-to-End Pipeline Entry Point:
    1. Retrieves subgraph context + supporting node metadata
    2. Synthesizes an answer using the LLM
    3. Combines results into the payload required by Nikshith's frontend
    """
    # 1. Retrieve subgraph context and supporting node metadata
    retrieval_output = retrieve_context(query=query, top_k=top_k)
    text_context = retrieval_output.get("text_context", "")
    supporting_nodes = retrieval_output.get("supporting_nodes", [])

    # 2. Synthesize natural language answer with LLM
    answer_text = synthesize_answer(query=query, text_context=text_context)

    # 3. Format API payload for frontend consumption
    return {
        "query": query,
        "answer": answer_text,
        "supporting_nodes": supporting_nodes
    }


if __name__ == "__main__":
    # Test execution block
    test_query = "What tools does AURA-KG use?"
    
    print(f"Executing full RAG pipeline for: '{test_query}'...\n")
    result = answer_query(test_query)

    print("=== SYNTHESIZED LLM ANSWER ===")
    print(result["answer"])

    print("\n=== SUPPORTING FRONTEND NODES ===")
    for node in result["supporting_nodes"]:
        print(node)