from fastapi import FastAPI, HTTPException
from ..application.dtos import UserMessage, BotResponse
from ..application.services import conversation_service

app = FastAPI(
    title="Asesor de Ventas para Clases de Guitarra",
    description="Microservicio que guía a los clientes a través de un proceso de venta y agendamiento.",
    version="1.0.0"
)

@app.post("/api/v1/lead", response_model=BotResponse)
async def process_message_endpoint(user_msg: UserMessage):
    try:
        response = conversation_service.process_message(user_msg)
        return response
    except Exception as e:
        # In a real app, you would log this error
        print(f"Error inesperado: {e}")
        raise HTTPException(status_code=500, detail=f"Ocurrió un error inesperado. Por favor, intenta de nuevo más tarde.")
