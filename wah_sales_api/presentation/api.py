from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # 👈 importar CORS
from ..application.dtos import UserMessage, BotResponse
from ..application.services import conversation_service

app = FastAPI(
    title="Asesor de Ventas para Clases de Guitarra",
    description="Microservicio que guía a los clientes a través de un proceso de venta y agendamiento.",
    version="1.0.0"
)

# 🚀 Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 👈 para pruebas, acepta cualquier origen
    allow_credentials=True,
    allow_methods=["*"],  # permitir todos los métodos (POST, GET, etc.)
    allow_headers=["*"],  # permitir todos los headers
)

@app.post("/api/v1/lead", response_model=BotResponse)
async def process_message_endpoint(user_msg: UserMessage):
    try:
        response = conversation_service.process_message(user_msg)
        return response
    except Exception as e:
        # En producción deberías loguear bien el error
        print(f"Error inesperado: {e}")
        raise HTTPException(
            status_code=500,
            detail="Ocurrió un error inesperado. Por favor, intenta de nuevo más tarde."
        )
