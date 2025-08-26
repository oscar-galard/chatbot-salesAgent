import os
import instructor
from openai import OpenAI
from dotenv import load_dotenv
from ..domain.models import PerfilInicial, PlanRecomendado, IntencionRespuesta, DatosAgendamiento, PerfilCompleto

class NLPService:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "tu_clave_de_api_aqui":
            print("ADVERTENCIA: La clave OPENAI_API_KEY no se ha configurado en el archivo .env. El servicio de NLP no funcionará.")
            self.client = None
        else:
            self.client = instructor.patch(OpenAI(api_key=api_key))

    def extract_initial_profile(self, message: str) -> PerfilInicial:
        return self.client.chat.completions.create(
            model="gpt-4o",
            response_model=PerfilInicial,
            messages=[
                {"role": "system", "content": "Extrae 'para quien son las clases' y la 'edad' de la respuesta del usuario."},
                {"role": "user", "content": message}
            ]
        )

    def recommend_plan(self, perfil: PerfilCompleto) -> PlanRecomendado:
        return self.client.chat.completions.create(
            model="gpt-4o",
            response_model=PlanRecomendado,
            messages=[
                {"role": "system", "content": "Eres un asistente de ventas. Con base en la motivación, objetivos y disponibilidad de tiempo del alumno, recomienda el plan 'basico', 'intermedio' o 'avanzado'. Usa 'basico' si el compromiso es bajo o el interés es exploratorio. Usa 'avanzado' si hay metas profesionales o alto compromiso."},
                {"role": "user", "content": f"Perfil del usuario: {perfil.model_dump_json()}"}
            ]
        )

    def generate_sales_pitch(self, perfil: PerfilCompleto, plan: dict) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Actúa como un asesor de ventas cálido y profesional de una escuela de música. Conecta la historia del usuario con los beneficios del plan recomendado. Haz que se sienta comprendido, motivado y entusiasmado. Sé breve pero efectivo. Termina con una invitación clara y amigable para agendar una clase muestra gratuita."},
                {"role": "user", "content": f"Aquí tienes el perfil del usuario:\n{perfil.model_dump_json()}\n\nEl plan recomendado es: '{plan['nombre']}'. Sus detalles son:\n{plan['descripcion']}. Precio: ${plan['precio']}."}
            ]
        )
        return response.choices[0].message.content

    def classify_intent(self, message: str) -> IntencionRespuesta:
        return self.client.chat.completions.create(
            model="gpt-4o",
            response_model=IntencionRespuesta,
            messages=[
                {"role": "system", "content": "Clasifica la respuesta del usuario. 'afirmativa' si quiere agendar, 'negativa' si no quiere."},
                {"role": "user", "content": message}
            ]
        )

    def extract_scheduling_data(self, message: str) -> DatosAgendamiento:
        return self.client.chat.completions.create(
            model="gpt-4o",
            response_model=DatosAgendamiento,
            messages=[
                {"role": "system", "content": "Extrae el número de teléfono, día y hora de la respuesta del usuario para agendar una sesión. El número de teléfono es un campo requerido. El día y la hora son opcionales."},
                {"role": "user", "content": message}
            ]
        )

nlp_service = NLPService()
