from typing import Dict, Optional
from .models import PerfilCompleto

PLANES_DATA: Dict[str, Dict[str, any]] = {
    "basico": {
        "nombre": "Descubre",
        "precio": 399,
        "descripcion": "2 clases teóricas y 2 laboratorios, duración 30 a 40 min. Perfecto para los que tienen poco tiempo a la semana, pero aún así quieren aprender.",
    },
    "intermedio": {
        "nombre": "Impulsa",
        "precio": 699,
        "descripcion": "4 clases teóricas y 2 laboratorios, duración 30 a 40 min. Para quienes quieren dedicar más tiempo a su aprendizaje, y la música es una parte más fundamental de su vida.",
    },
    "avanzado": {
        "nombre": "Domina",
        "precio": 999,
        "descripcion": "4 clases teóricas y 4 laboratorios, duración 30 a 40 min. Para los que quieren dedicar su vida a la música, ya sea para ser profesionales, dar clases o preparar un examen de ingreso a la escuela.",
    },
    "definiciones": {
        "laboratorio": "Es una sesión enfocada en la práctica y el desarrollo de un proyecto, como una canción, un riff o una composición propia. Es un espacio para aplicar la teoría de las clases de manera creativa.",
    }
}

def get_pregunta_motivacion(para_quien: str) -> str:
    para_quien_text = para_quien.lower()
    palabras_yo = ["yo", "mi", "mí", "mismo"]
    plurales = ["hijas", "hijos", "nietos", "amigos", "ellos", "niños", "alumnos"]

    if any(p in para_quien_text.split() for p in palabras_yo):
        return "¿qué te inspira a aprender a tocar la guitarra y qué te gustaría lograr con ella?"
    
    es_plural = any(p in para_quien_text.split() for p in plurales) or para_quien_text.endswith('s')
    
    if es_plural:
        para_quien_natural = para_quien.replace("mi ", "tus ")
        return f"¿qué les inspira a {para_quien_natural} a aprender a tocar la guitarra y qué les gustaría lograr con ella?"
    else:
        para_quien_natural = para_quien.replace("mi ", "tu ")
        return f"¿qué le inspira a {para_quien_natural} a aprender a tocar la guitarra y qué le gustaría lograr con ella?"

def recommend_plan_by_age(perfil: PerfilCompleto) -> Optional[str]:
    if perfil.edad < 11:
        return "basico"
    return None
