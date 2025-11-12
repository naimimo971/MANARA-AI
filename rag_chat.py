import os
import numpy as np
import faiss
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, CrossEncoder
from openai import OpenAI

load_dotenv()

INDEX_DIR = os.getenv("INDEX_DIR", "./kb_index")

# Global variables (lazy loaded)
_rag_cache = {}

def get_api_key():
    """Get API key from Streamlit secrets or environment variables."""
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
            return st.secrets['OPENAI_API_KEY']
    except:
        pass
    
    # Fallback to environment variable
    return os.getenv('OPENAI_API_KEY')

def get_rag_components():
    """Get or initialize RAG components (cached)."""
    global _rag_cache
    
    if "initialized" in _rag_cache:
        return _rag_cache
    
    # Get API key
    OPENAI_API_KEY = get_api_key()
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY missing. Please set it in Streamlit secrets or .env file")
    
    # Initialize components
    client = OpenAI(api_key=OPENAI_API_KEY)
    emb = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    
    # Load index with error handling
    try:
        index_path = os.path.join(INDEX_DIR, "faiss.index")
        texts_path = os.path.join(INDEX_DIR, "texts.npy")
        sources_path = os.path.join(INDEX_DIR, "sources.npy")
        
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"FAISS index not found at {index_path}")
        
        index = faiss.read_index(index_path)
        texts = np.load(texts_path, allow_pickle=True)
        sources = np.load(sources_path, allow_pickle=True)
        
    except Exception as e:
        raise RuntimeError(f"Failed to load RAG index: {str(e)}")
    
    _rag_cache = {
        "client": client,
        "emb": emb,
        "reranker": reranker,
        "index": index,
        "texts": texts,
        "sources": sources,
        "initialized": True
    }
    
    print(f"Total chunks indexed: {len(texts)}")
    print("Sample sources:", sources[:5])
    
    return _rag_cache

# In rag_chat.py - UPDATE THE SYSTEM PROMPT
SYS_PROMPT = (
    "You are Manara, a friendly bilingual assistant for Applied Technology Schools (ATS) in UAE. "
    "Answer questions based on the provided context. "
    "**Language Rule: Respond in the same language the question was asked in. If Arabic, answer in Arabic. If English, answer in English. Never mix languages.** "
    "Be helpful and provide information from the context when available. "
    "Keep answers concise (2-4 sentences). "
    "If the context doesn't have the exact answer, use related information to provide a helpful response. "
    "Only say you don't have information if the context is completely irrelevant to the question."
)

def truncate_chunk(txt: str, max_words: int = 200) -> str:
    words = txt.split()
    if len(words) > max_words:
        return " ".join(words[:max_words]) + "… (truncated)"
    return txt

def retrieve(query: str, k: int = 30, top_n: int = 5):
    """Retrieve and re-rank the most relevant chunks."""
    try:
        rag = get_rag_components()
        emb = rag["emb"]
        reranker = rag["reranker"]
        index = rag["index"]
        texts = rag["texts"]
        sources = rag["sources"]
        
        # 1. Initial retrieval (vector search)
        q = emb.encode([query], normalize_embeddings=True)
        D, I = index.search(q, k)
        
        initial_ctx = []
        for i, score in zip(I[0], D[0]):
            if i == -1:
                continue
            initial_ctx.append({"text": texts[i], "source": sources[i], "score": float(score)})
            
        if not initial_ctx:
            return []

        # 2. Re-ranking (cross-encoder)
        sentences = [c["text"] for c in initial_ctx]
        pairs = [[query, sentence] for sentence in sentences]
        
        # The CrossEncoder returns a score for each pair
        scores = reranker.predict(pairs)
        
        # Sort the initial context based on the re-ranker scores
        reranked_ctx = sorted(
            zip(initial_ctx, scores),
            key=lambda x: x[1],
            reverse=True
        )
        
        # 3. Select the top_n chunks
        final_ctx = []
        for (ctx_item, score) in reranked_ctx[:top_n]:
            # Update the score to the re-ranker score for transparency
            ctx_item["score"] = float(score)
            final_ctx.append(ctx_item)
            
        return final_ctx
    except Exception as e:
        print(f"Error in retrieve function: {e}")
        return []

def answer(query: str, history):
    """Generate an answer using RAG with GPT-4o-mini."""
    try:
        rag = get_rag_components()
        client = rag["client"]
        
        # Use the retrieve function with re-ranking.
        # It retrieves 30 candidates and re-ranks to the top 5 for quality context.
        ctx = retrieve(query, k=30, top_n=5)
        
        # If no context is found, return a polite "I don't know" message
        if not ctx:
            return "I am sorry, but I cannot find the answer to your question in the provided documents. Please try asking about admissions, fees, curriculum, locations, or other ATS-related topics."

        short_ctx = [truncate_chunk(c["text"]) for c in ctx]

        joined = "\n---\n".join(
            f"{txt}"
            for i, (c, txt) in enumerate(zip(ctx, short_ctx))
        )

        # More direct prompt without encouraging reasoning
        prompt = (
            f"Context information:\n{joined}\n\n"
            f"Question: {query}\n\n"
            f"Using the context above, provide a helpful answer to the question. "
            f"**Important: Answer in the exact same language as the question.** "
            f"If the question is in Arabic, answer entirely in Arabic. "
            f"If the question is in English, answer entirely in English. "
            f"Be friendly and conversational. "
            f"Use the context information to provide the best possible answer. "
            f"If the context contains relevant information, use it to answer. "
            f"Only say you cannot find the answer if the context is completely unrelated. "
            f"Keep it brief (2-4 sentences). "
            f"Do not mention file names or sources."
        )

        resp = client.chat.completions.create(
            model="gpt-4o-mini",  # Fixed model name
            messages=[
                {"role": "system", "content": SYS_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=300,
        )
        return resp.choices[0].message.content
    except Exception as e:
        print(f"Error in answer function: {e}")
        return f"I encountered an error while processing your request. Please try again. Error: {str(e)}"
    