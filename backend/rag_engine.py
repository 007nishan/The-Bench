import os
import json
import math
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
# Defer validation - don't crash on import if missing
# if not API_KEY:
#     raise ValueError("GOOGLE_API_KEY not found in .env")

# --- Direct REST API Helper ---

def call_gemini_generate(prompt: str):
    # Using 'gemini-flash-latest' as it appears in the available models list
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print(f"Generate Error: {e}")
        if response.content:
            print(f"Error Details: {response.content.decode()}")
        return f"Error generating content: {str(e)}"

def call_gemini_embed(text: str, task_type="retrieval_document"):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/embedding-001:embedContent?key={API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "models/embedding-001",
        "content": {"parts": [{"text": text}]},
        "taskType": task_type.upper(),
        "title": "Embedded Document" if task_type == "retrieval_document" else None
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        return response.json()['embedding']['values']
    except Exception as e:
        print(f"Embed Error: {e}")
        if response.content:
            print(f"Error Details: {response.content.decode()}")
        return []

# --- Simple JSON Vector Store Implementation ---
DB_FILE = "vector_store.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {"accuser_vault": [], "accused_vault": [], "judge_vault": [], "common_vault": []}

def save_db(db):
    try:
        with open(DB_FILE, "w") as f:
            json.dump(db, f, indent=2)
    except Exception as e:
        print(f"Error saving DB: {e}")

def cosine_similarity(v1, v2):
    if not v1 or not v2: return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    magnitude1 = math.sqrt(sum(a * a for a in v1))
    magnitude2 = math.sqrt(sum(b * b for b in v2))
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    return dot_product / (magnitude1 * magnitude2)

# --- Public API ---

def store_document(role: str, doc_id: str, text: str, meta: dict = None):
    print(f"DEBUG: Storing document {doc_id} for {role}")
    db = load_db()
    vault_name = f"{role}_vault"
    if vault_name not in db:
        db[vault_name] = []
    
    embedding = call_gemini_embed(text, task_type="retrieval_document")
    
    if not embedding:
        print("ERROR: Failed to generate embedding for storage")
        return {"status": "error", "message": "Embedding failed"}

    doc = {
        "id": doc_id,
        "text": text,
        "embedding": embedding,
        "meta": meta or {"source": "manual"}
    }
    
    db[vault_name].append(doc)
    save_db(db)
    print("DEBUG: Document stored successfully")
    return {"status": "success", "doc_id": doc_id}

def retrieve_context(role: str, query: str, n_results: int = 3):
    print(f"DEBUG: Retrieving context via REST for {role}: {query}")
    db = load_db()
    
    q_embedding = call_gemini_embed(query, task_type="retrieval_query")
    if not q_embedding:
        return "(Error retrieving context: Embedding failed)"
    
    results = []
    vaults_to_search = [f"{role}_vault", "common_vault"]
    
    for v_name in vaults_to_search:
        if v_name in db:
            for doc in db[v_name]:
                score = cosine_similarity(q_embedding, doc['embedding'])
                results.append({
                    "text": doc['text'],
                    "meta": doc.get('meta', {}),
                    "score": score,
                    "type": "PRIVATE" if role in v_name else "PUBLIC"
                })

    results.sort(key=lambda x: x['score'], reverse=True)
    top_results = results[:n_results]
    
    context_text = ""
    for r in top_results:
        context_text += f"\n[{r['type']} | Score: {r['score']:.2f}]\n{r['text']}\n"
        
    if not context_text:
        context_text = "(No relevant documents found.)"
        
    print(f"DEBUG: Context found: {len(top_results)} items")
    return context_text

def generate_strategic_response(role: str, query: str):
    print(f"DEBUG: Generating strategy via REST for {role}...")
    context = retrieve_context(role, query)
    
    personas = {
        "accuser": "You are a Zealous Prosecutor. Maximize liability. Be aggressive.",
        "accused": "You are a Defensive Strategist. Minimize liability. Deny everything.",
        "judge": "You are a Neutral Arbiter. Strictly verify facts."
    }
    
    prompt = f"""
    SYSTEM: {personas.get(role, "Legal Assistant")}
    
    CONTEXT (Retrieved Evidence):
    {context}
    
    USER QUERY: {query}
    
    INSTRUCTIONS:
    - Use the Context to back up your arguments.
    - If the user query is unrelated to context, use general legal principles.
    - Keep responses concise and strategic.
    """
    
    return call_gemini_generate(prompt)
