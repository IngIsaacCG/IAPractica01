import re
import json
from pathlib import Path

reglas = [
    ('CLAVE', r'\b[0-9][0-9][0-9][0-9]\b'),
    ('SEMESTRE_NUM', r'\b[1-9]\b'),
    ('INT_SERIACION', r'\b(seriacion|requisitos?|prerrequisitos?|antecedentes?|consecuentes?|cadena|abre)\b'),
    ('INT_CREDITOS', r'\b(creditos?|carga|valor)\b'),
    ('INT_TEMARIO', r'\b(temario|temas|contenido|objetivo)\b'),
    ('MATERIA_NOMBRE', r'\b(fundamentos de programacion|estructuras? de datos|algebra|sistemas operativos)\b'),
    ('SALUDO', r'\b(hola|buenas?|que tal)\b'),
    ('DESPEDIDA', r'\b(adios|salir|chao|bye)\b'),
    ('SKIP', r'[,\.\?\!\s]+'),  
    ('MISC', r'.'),            
]

def rutaJson(semestrePeticion)
    peticion = semestrePeticion
    rutaPrograma = Path(__file__).resolve().parent.parent
    RUTA_JSON = rutaPrograma / "json" / "quintoSemestre.json"

def cambioMayusculasMinusculas():
    entrada = input("Holas soy tu asistente para escoger materias, ¿en que te puedo ayudar? ")
    return entrada.lower()


def main():
    semestrePeticion = 
    peticion = cambioMayusculasMinusculas()
    rutaJson(semestrePeticion)
    return 0

if __name__ == "__main__":
    main()