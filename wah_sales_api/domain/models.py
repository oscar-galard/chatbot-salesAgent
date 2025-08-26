from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional, Dict, Any
import re

class PerfilInicial(BaseModel):
    para_quien: str = Field(..., description="A quién están dirigidas las clases.")
    edad: Optional[int] = Field(None, description="La edad de la persona que tomará las clases.")
    
    @field_validator('edad', mode='before')
    def parse_edad(cls, v):
        if v is None:
            return -1
        return v

class PerfilCompleto(BaseModel):
    para_quien: str = Field(..., description="A quién están dirigidas las clases.")
    edad: int = Field(..., description="La edad de la persona que tomará las clases.")
    motivacion: str = Field(..., description="La razón principal para querer aprender a tocar la guitarra.")
    objetivo: str = Field(..., description="Lo que el usuario espera lograr con las clases.")
    tiempo_disponible: str = Field(..., description="El tiempo semanal que el usuario puede dedicar a las clases.")
    
    @field_validator('edad')
    def validar_edad(cls, v):
        if v <= 0:
            raise ValueError('La edad debe ser un número positivo.')
        return v

class PlanRecomendado(BaseModel):
    plan_recomendado: Literal["basico", "intermedio", "avanzado"] = Field(
        ..., description="Recomienda el plan que mejor se adapte a la motivación del usuario."
    )

class DatosAgendamiento(BaseModel):
    numero_telefono: str = Field(
        ..., 
        description="El número de teléfono del usuario.",
        pattern=r'^\+?(\d{1,3})?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$'
    )
    dia_preferido: Optional[str] = Field(None, description="El día preferido para la sesión de prueba.")
    hora_preferida: Optional[str] = Field(None, description="La hora preferida para la sesión de prueba.")
    
    @field_validator('numero_telefono')
    def validar_numero_telefono(cls, v):
        if not re.match(r'^\+?(\d{1,3})?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$', v):
            raise ValueError('El formato del número de teléfono no es válido.')
        return v

class IntencionRespuesta(BaseModel):
    intencion: Literal["afirmativa", "negativa", "neutral"] = Field(
        ..., 
        description="Clasifica la respuesta del usuario. 'afirmativa' si acepta, 'negativa' si rechaza, 'neutral' si es ambigua."
    )

class Plan(BaseModel):
    nombre: str
    precio: int
    descripcion: str

class SessionData(BaseModel):
    session_id: str
    phase: str
    perfil_completo: Dict[str, Any] = {}
    propuesta_venta: Optional[str] = None
