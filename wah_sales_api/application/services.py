import re
from ..domain.models import SessionData, PerfilCompleto, Plan
from ..domain.services import get_pregunta_motivacion, recommend_plan_by_age, PLANES_DATA
from ..infrastructure.nlp_service import nlp_service
from ..infrastructure.session_storage import session_storage
from .dtos import UserMessage, BotResponse
from pydantic import ValidationError

class ConversationService:
    def process_message(self, user_msg: UserMessage) -> BotResponse:
        session = session_storage.get_session(user_msg.session_id)
        if not session:
            session = SessionData(session_id=user_msg.session_id, phase="ask_connect_1")
            session_storage.save_session(session)
            return BotResponse(
                session_id=session.session_id,
                response="¡Hola! Estoy aquí para ayudarte a encontrar el plan de guitarra perfecto para ti o tu familia. 😊\n"
                         "Para empezar, ¿para quién serían las clases y qué edad tiene esa persona (o personas)?",
                phase=session.phase
            )

        # Dispatch to the correct phase handler
        handler_method = getattr(self, f"_handle_{session.phase}", self._handle_unknown_phase)
        return handler_method(user_msg.message, session)

    def _handle_unknown_phase(self, message: str, session: SessionData) -> BotResponse:
        return BotResponse(session_id=session.session_id, response="Fase de sesión no válida. Reinicia la conversación.", phase="error")

    def _handle_ask_connect_1(self, message: str, session: SessionData) -> BotResponse:
        try:
            perfil_inicial = nlp_service.extract_initial_profile(message)
            session.perfil_completo["para_quien"] = perfil_inicial.para_quien
            
            if perfil_inicial.edad == -1:
                session.phase = "ask_connect_1_edad"
                session_storage.save_session(session)
                return BotResponse(
                    session_id=session.session_id,
                    response=f"No pude identificar la edad de {perfil_inicial.para_quien}. ¿Podrías confirmármela?",
                    phase=session.phase,
                    data={"perfil": session.perfil_completo}
                )

            session.perfil_completo["edad"] = perfil_inicial.edad
            pregunta_motivacion = get_pregunta_motivacion(perfil_inicial.para_quien)
            session.phase = "ask_connect_2"
            session_storage.save_session(session)
            return BotResponse(
                session_id=session.session_id,
                response=f"¡Genial! Ahora, cuéntame: {pregunta_motivacion}",
                phase=session.phase,
                data={"perfil": session.perfil_completo}
            )
        except Exception as e:
            return BotResponse(session_id=session.session_id, response=f"Error en la fase 1: {str(e)}. Por favor, responde de forma más clara.", phase=session.phase)

    def _handle_ask_connect_1_edad(self, message: str, session: SessionData) -> BotResponse:
        try:
            edad = int(re.search(r'\d+', message).group())
            session.perfil_completo["edad"] = edad
            
            para_quien = session.perfil_completo["para_quien"]
            pregunta_motivacion = get_pregunta_motivacion(para_quien)
            session.phase = "ask_connect_2"
            session_storage.save_session(session)
            return BotResponse(
                session_id=session.session_id,
                response=f"¡Gracias! Ahora, cuéntame: {pregunta_motivacion}",
                phase=session.phase,
                data={"perfil": session.perfil_completo}
            )
        except (ValueError, AttributeError):
            return BotResponse(
                session_id=session.session_id,
                response="Por favor, introduce la edad como un número (ej. '10 años').",
                phase=session.phase,
                data={"perfil": session.perfil_completo}
            )

    def _handle_ask_connect_2(self, message: str, session: SessionData) -> BotResponse:
        session.perfil_completo["motivacion"] = message
        session.perfil_completo["objetivo"] = message
        session.phase = "ask_connect_3"
        session_storage.save_session(session)
        return BotResponse(
            session_id=session.session_id,
            response="¿Y cuánto tiempo a la semana le pueden dedicar al aprendizaje?",
            phase=session.phase,
            data={"perfil": session.perfil_completo}
        )

    def _handle_ask_connect_3(self, message: str, session: SessionData) -> BotResponse:
        session.perfil_completo["tiempo_disponible"] = message
        
        try:
            perfil_validado = PerfilCompleto(**session.perfil_completo)
        except ValidationError as e:
            session_storage.delete_session(session.session_id)
            return BotResponse(session_id=session.session_id, response=f"Error al consolidar el perfil: {str(e)}. Reiniciando la conversación.", phase="error")

        plan_key = recommend_plan_by_age(perfil_validado) or nlp_service.recommend_plan(perfil_validado).plan_recomendado
        plan_info = PLANES_DATA[plan_key]
        
        propuesta = nlp_service.generate_sales_pitch(perfil_validado, plan_info)
        
        session.phase = "propose_plan"
        session.propuesta_venta = propuesta
        session_storage.save_session(session)
        
        return BotResponse(
            session_id=session.session_id,
            response=f"Analizando tu perfil para encontrar el plan ideal...\n\n🎸 Propuesta personalizada para ti:\n\n{propuesta}\n\n¿Te gustaría agendar una clase muestra gratuita? Responde de forma afirmativa o negativa:",
            phase=session.phase,
            data={"perfil": perfil_validado.model_dump(), "plan_recomendado": plan_info}
        )

    def _handle_propose_plan(self, message: str, session: SessionData) -> BotResponse:
        intencion = nlp_service.classify_intent(message).intencion
        
        if intencion == "afirmativa":
            session.phase = "agenda_1"
            session_storage.save_session(session)
            return BotResponse(
                session_id=session.session_id,
                response="¡Excelente! Por favor, danos tu número de teléfono, día y hora preferidos para contactarte y confirmar.",
                phase=session.phase
            )
        else:
            session_storage.delete_session(session.session_id)
            return BotResponse(
                session_id=session.session_id,
                response="Entendido. Si cambias de opinión, no dudes en contactarnos. ¡Que tengas un excelente día!",
                phase="closed"
            )

    def _handle_agenda_1(self, message: str, session: SessionData) -> BotResponse:
        try:
            datos = nlp_service.extract_scheduling_data(message)
            print(f"Datos de agendamiento recibidos para la sesión {session.session_id}: {datos.model_dump_json()}")
            
            session_storage.delete_session(session.session_id)
            return BotResponse(
                session_id=session.session_id,
                response="¡Listo! Hemos recibido tu información. Te contactaremos pronto para confirmar los detalles de tu clase muestra.",
                phase="closed",
                data={"agendamiento": datos.model_dump()}
            )
        except Exception as e:
            return BotResponse(
                session_id=session.session_id,
                response=f"No pude extraer la información de agendamiento. Por favor, asegúrate de incluir tu número de teléfono, día y hora. Error: {e}",
                phase=session.phase
            )

conversation_service = ConversationService()
