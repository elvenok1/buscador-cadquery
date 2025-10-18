import os
from fastapi import FastAPI
from pydantic import BaseModel
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import warnings
import urllib3
from typing import List, Dict, Any

# Ignoramos advertencias de seguridad
warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)

# --- 1. CONFIGURACIÓN PARA CADQUERY ---
QDRANT_IP = "209.126.82.74"
QDRANT_HOSTNAME = "soluciones-qdrant.vh0e8b.easypanel.host"
MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'
    
# <<< ¡¡CAMBIO MÁS IMPORTANTE!! Apuntamos a la nueva colección de CadQuery
COLLECTION_NAME = "cadquery_semantic_v1" 

# --- Carga de recursos globales ---
print("Cargando el modelo de embeddings...")
model = SentenceTransformer(MODEL_NAME)
print("Modelo cargado exitosamente.")

print("Estableciendo conexión con Qdrant...")
client = QdrantClient(
        host=QDRANT_IP, port=443, https=True, verify=False,
        prefer_grpc=False, headers={"Host": QDRANT_HOSTNAME}, timeout=20
)
# Verificamos que la nueva colección existe
client.get_collection(collection_name=COLLECTION_NAME)
print(f"Conexión exitosa. Colección '{COLLECTION_NAME}' encontrada.")
    
# --- Modelos de datos Pydantic ---
class SearchResult(BaseModel):
        id: str
        score: float
        payload: Dict[str, Any]

class SearchResponse(BaseModel):
        status: str
        resultados: List[SearchResult]

# --- Inicialización de FastAPI ---
app = FastAPI(
        title="API de Búsqueda Semántica para CadQuery",
        description="Un servicio para encontrar ejemplos de código y documentación de CadQuery."
)

# --- Endpoint de Búsqueda ---
@app.get("/buscar", response_model=SearchResponse)
async def search_cadquery_docs(question: str, top_k: int = 3):
        print(f"Recibida pregunta para CadQuery: '{question}'")
        
        vector_pregunta = model.encode(question).tolist()
        
        search_results_raw = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=vector_pregunta,
            limit=top_k,
            with_payload=True 
)
        
        resultados_limpios = [
            SearchResult(id=str(hit.id), score=hit.score, payload=hit.payload) 
            for hit in search_results_raw
        ]
        
        return SearchResponse(status="success", resultados=resultados_limpios)

@app.get("/")
def read_root():
        return {"status": "Servicio de búsqueda de CadQuery activo."}


