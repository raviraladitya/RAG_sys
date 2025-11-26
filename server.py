import os
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
import google.generativeai as genai
from typing import List

# --- CONFIGURATION ---
# Get your key from https://aistudio.google.com/
os.environ["GEMINI_API_KEY"] = "AIzaSyDQQCf0pFmDESvVJs6N-7d3jVKdEZ2d4hw" 

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# --- CUSTOM EMBEDDING FUNCTION FOR CHROMA ---
class GeminiEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        model = "models/text-embedding-004"
        # Create embeddings for the list of texts
        response = genai.embed_content(
            model=model,
            content=input,
            task_type="retrieval_document",
            title="NebulaGears Policy"
        )
        return response['embedding']

# --- INITIALIZE DB & LLM ---
def setup_rag_system():
    # 1. Initialize ChromaDB (Local - Ephemeral for this script, or use PersistentClient to save to disk)
    chroma_client = chromadb.Client()
    
    # 2. Create Collection with Gemini Embeddings
    collection = chroma_client.create_collection(
        name="nebula_gears_policies",
        embedding_function=GeminiEmbeddingFunction()
    )

    # 3. The Dataset (Conflicting Documents)
    documents = [
        "At NebulaGears, we believe in complete freedom. All employees are eligible for the 'Work From Anywhere' program. You can work remotely 100% of the time from any location. No prior approval is needed.",
        "Update to remote work policy: Effective immediately, remote work is capped at 3 days per week. Employees must be in the HQ office on Tuesdays and Thursdays. All remote days require manager approval.",
        "Welcome to the team! Please note that while full-time employees have hybrid options, interns are required to be in the office 5 days a week for the duration of their internship to maximize mentorship. No remote work is permitted for interns."
    ]
    
    metadatas = [
        {"source": "employee_handbook_v1.txt", "type": "general_policy"},
        {"source": "manager_updates_2024.txt", "type": "update"},
        {"source": "intern_onboarding_faq.txt", "type": "role_specific"}
    ]
    
    ids = ["doc_a", "doc_b", "doc_c"]

    # 4. Ingest Data
    collection.add(documents=documents, metadatas=metadatas, ids=ids)
  
    
    return collection

# --- QUERY LOGIC ---
def query_rag(collection, user_query):
    # 1. Retrival (We conider the all three files, in fact top  3 relevant files to ensure we get the conflicting contexts)
    results = collection.query(
        query_texts=[user_query],
        n_results=3 
    )
    
    # 2. Construct Context String
    context_text = ""
    for i, doc in enumerate(results['documents'][0]):
        source = results['metadatas'][0][i]['source']
        context_text += f"SOURCE: {source}\nCONTENT: {doc}\n\n"

    # 3. The "Conflict Logic" Prompt
    system_instruction = """
    you have to answer user queries but there are conflict in the documents for the queries, so i'll provide you with some set of instructions and using those instructions you have to provide the answers by proritizing them.
    
    solving the conflicting policies by the follwing rules:
    1. Specificity Overrides General: Rules for specific roles (e.g., Interns) should override general employee rules.
    2. Recency Overrides : If policies clash for the same group, consider the document which is recently updated.
    3. Citation: explicitly mention to cite the source filename that dictates the final decision.
    
    If the user is an Intern, the Intern FAQ rules apply regardless of general policies.
    """

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash", 
        system_instruction=system_instruction
    )

    prompt = f"Context:\n{context_text}\n\nUser Question: {user_query}"

    response = model.generate_content(prompt)
    return response.text

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    collection = setup_rag_system()
    
    # The Scenario Question
    query = "As a full-time employee, how many days can I work remotely"
    print(f"\n❓ User query: {query}")
    
    answer = query_rag(collection, query)  
    
    print("\n🤖 Gemini response:")
    print("-" * 30)
    print(answer)
    print("-" * 30)