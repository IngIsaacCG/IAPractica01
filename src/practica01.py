import re
import json
from pathlib import Path


# --- 1. ESTRUCTURAS DE DATOS (POO) Y LEXER ---


class Token:
    def __init__(self, tipo: str, valor: str):
        self.tipo = tipo
        self.valor = valor

    def __repr__(self):
        return f"Token({self.tipo}, '{self.valor}')"


class Lexer:
    def __init__(self, reglas: list[tuple[str, str]]):
        self.reglas = reglas
        self.regex = "|".join(
            f"(?P<{nombre}>{patron})" for nombre, patron in self.reglas
        )

    def tokenizar(self, texto: str) -> list[Token]:
        tokens = []
        for match in re.finditer(self.regex, texto):
            tipo = match.lastgroup
            valor = match.group()

            # Descartar puntuación, espacios y caracteres no reconocidos
            if tipo in ("SKIP", "MISC"):
                continue

            tokens.append(Token(tipo, valor))

        return tokens


# ---RUTAS Y CARGA DE DATOS JSON ---


def obtener_ruta_json(semestre: int) -> Path:
    mapa_archivos = {
        1: "primerSemestre.json",
        2: "segundoSemestre.json",
        3: "tercerSemestre.json",
        4: "cuartoSemestre.json",
        5: "quintoSemestre.json",
        6: "sextoSemestre.json",
        7: "septimoSemestre.json",
        8: "octavoSemestre.json",
    }

    nombre_archivo = mapa_archivos.get(semestre, f"semestre{semestre}.json")
    ruta_raiz_repo = Path(__file__).resolve().parent.parent
    return ruta_raiz_repo / "json" / nombre_archivo


def cargar_base_datos(semestre: int) -> list[dict]:
    ruta_json = obtener_ruta_json(semestre)
    try:
        with open(ruta_json, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


# ---ALGORITMOS DE BÚSQUEDA POR SCORING ---


def buscar_materia_por_scoring(materias: list[dict], texto: str) -> dict | None:
    texto_limpio = texto.lower()
    mejor_materia = None
    mayor_puntaje = 0

    for materia in materias:
        nombre = materia.get("nombre", "").lower()
        puntaje = 0

        # Sumar puntos por coincidencias individuales de palabras con más de 3 letras
        for palabra in nombre.split():
            if len(palabra) > 3 and palabra in texto_limpio:
                puntaje += 1

        # Sumar bonificación por coincidencia exacta de la frase
        if nombre in texto_limpio:
            puntaje += 10

        if puntaje > mayor_puntaje:
            mayor_puntaje = puntaje
            mejor_materia = materia

    return mejor_materia


def buscar_subtemas_en_materia(
    materia: dict, texto: str
) -> tuple[dict | None, list[str]]:
    texto_limpio = texto.lower()
    mejor_tema = None
    mayor_puntaje = 0

    temario = materia.get("temario", [])
    for tema in temario:
        nombre_tema = tema.get("nombre", "").lower()
        puntaje = 0

        for palabra in nombre_tema.split():
            if len(palabra) > 3 and palabra in texto_limpio:
                puntaje += 1

        if nombre_tema in texto_limpio:
            puntaje += 10

        if puntaje > mayor_puntaje:
            mayor_puntaje = puntaje
            mejor_tema = tema

    if mejor_tema:
        return mejor_tema, mejor_tema.get("subtemas", [])

    return None, []


# ---ANALIZADOR SEMÁNTICO Y RESPUESTA ---


def analizador_semantico(tokens: list[Token]):
    intenciones = []
    clave = None
    materia_nombre = None
    semestre = None

    mapa_semestres_texto = {
        "primer semestre": 1,
        "segundo semestre": 2,
        "tercer semestre": 3,
        "cuarto semestre": 4,
        "quinto semestre": 5,
        "sexto semestre": 6,
        "septimo semestre": 7,
        "séptimo semestre": 7,
        "octavo semestre": 8,
    }

    for token in tokens:
        if token.tipo.startswith("INT_"):
            intenciones.append(token.tipo)
        elif token.tipo == "CLAVE":
            clave = token.valor
        elif token.tipo == "MATERIA_NOMBRE":
            materia_nombre = token.valor
        elif token.tipo == "SEMESTRE_NUM":
            semestre = int(token.valor)
        elif token.tipo == "SEMESTRE_TEXTO":
            semestre = mapa_semestres_texto.get(token.valor)

    return intenciones, clave, materia_nombre, semestre


def consultar_y_responder(
    intenciones: list[str],
    clave: str,
    materia_nombre: str,
    semestre: int,
    texto_original: str,
    contexto: dict,
) -> str:
    # Actualizar o recuperar el semestre almacenado en contexto
    if semestre:
        contexto["semestre_actual"] = semestre
    else:
        semestre = contexto.get("semestre_actual")

    # Caso 1: Listado general de materias de un semestre determinado
    if (
        "INT_SEMESTRE_LISTA" in intenciones
        and semestre
        and not materia_nombre
        and not clave
    ):
        base_datos = cargar_base_datos(semestre)
        if not base_datos:
            return f"No encontré información cargada para el semestre {semestre}."

        respuestas = [f"--- MATERIAS REGISTRADAS PARA EL SEMESTRE {semestre} ---"]
        for m in base_datos:
            respuestas.append(
                f"• Clave {m['clave']}: {m['nombre']} ({m.get('creditos', 'N/A')} créditos)"
            )
        return "\n".join(respuestas)

    # Buscar la materia en el semestre en contexto o en todo el plan de estudios
    materia_encontrada = None
    if semestre:
        materias_sem = cargar_base_datos(semestre)
        if clave:
            materia_encontrada = next(
                (m for m in materias_sem if str(m.get("clave")) == str(clave)), None
            )
        if not materia_encontrada:
            materia_encontrada = buscar_materia_por_scoring(
                materias_sem, texto_original
            )
    else:
        for sem in range(1, 9):
            materias_sem = cargar_base_datos(sem)
            if clave:
                materia_encontrada = next(
                    (m for m in materias_sem if str(m.get("clave")) == str(clave)), None
                )
            if not materia_encontrada:
                materia_encontrada = buscar_materia_por_scoring(
                    materias_sem, texto_original
                )

            if materia_encontrada:
                contexto["semestre_actual"] = sem
                break

    if not materia_encontrada:
        if semestre:
            return f"No encontré esa materia en el semestre {semestre}."
        return "No encontré esa materia en el plan de estudios."

    # Guardar materia encontrada en memoria de contexto
    contexto["materia_actual"] = materia_encontrada

    # Caso 2: Consulta específica de subtemas dentro de un tema
    if "INT_SUBTEMA" in intenciones:
        tema, subtemas = buscar_subtemas_en_materia(materia_encontrada, texto_original)
        if tema and subtemas:
            respuestas = [
                f"--- Subtemas de '{tema['nombre']}' ({materia_encontrada['nombre']}) ---"
            ]
            for st in subtemas:
                respuestas.append(f"• {st}")
            return "\n".join(respuestas)
        elif tema:
            return f"El tema '{tema['nombre']}' no tiene subtemas registrados."
        return f"No encontré el tema especificado dentro de {materia_encontrada['nombre']}."

    # Caso 3: Respuesta con los campos solicitados o ficha general
    respuestas = [
        f"--- Información de: {materia_encontrada['nombre']} (Clave: {materia_encontrada['clave']}) ---"
    ]

    tiene_intencion = any(
        i in intenciones for i in ["INT_TEMARIO", "INT_SERIACION", "INT_CREDITOS"]
    )
    if not tiene_intencion:
        respuestas.append(f"• Créditos: {materia_encontrada.get('creditos', 'N/A')}")
        respuestas.append(f"• Modalidad: {materia_encontrada.get('modalidad', 'N/A')}")
        if "objetivo" in materia_encontrada:
            respuestas.append(f"• Objetivo: {materia_encontrada['objetivo']}")

    for intencion in intenciones:
        if intencion == "INT_SERIACION":
            seriacion = materia_encontrada.get("seriacion", {})
            ant = seriacion.get("antecedente", "Ninguna")
            cons = seriacion.get("consecuente", "Ninguna")
            respuestas.append(
                f"• Seriación:\n  - Antecedente: {ant}\n  - Consecuente: {cons}"
            )

        elif intencion == "INT_CREDITOS":
            respuestas.append(
                f"• Créditos: {materia_encontrada.get('creditos', 'No disponible')}"
            )

        elif intencion == "INT_TEMARIO":
            temario = materia_encontrada.get("temario", [])
            if temario:
                respuestas.append("• Temario principal:")
                for tema in temario:
                    respuestas.append(
                        f"  {tema.get('num', '-')}. {tema.get('nombre', 'Tema')} ({tema.get('horas', 0)} hrs)"
                    )

    return "\n".join(respuestas)


# ---FLUJO PRINCIPAL DE EJECUCIÓN (REPL) ---


def main():
    # Tabla de reglas
    reglas = [
        ("CLAVE", r"\b[0-9]{4}\b"),
        ("SEMESTRE_NUM", r"\b[1-9]\b"),
        (
            "SEMESTRE_TEXTO",
            r"\b(primer|segundo|tercer|cuarto|quinto|sexto|septimo|séptimo|octavo)\s+semestre\b",
        ),
        (
            "INT_SERIACION",
            r"\b(seriacion|requisitos?|prerrequisitos?|antecedentes?|consecuentes?|cadena|abre)\b",
        ),
        ("INT_CREDITOS", r"\b(creditos?|carga|valor)\b"),
        ("INT_TEMARIO", r"\b(temario|temas|contenido|objetivo)\b"),
        ("INT_SUBTEMA", r"\b(subtema|subtemas)\b"),
        (
            "INT_SEMESTRE_LISTA",
            r"\b(materias?|asignaturas?|clases?|ver?|se ve|cursa|cursan|lista)\b",
        ),
        (
            "MATERIA_NOMBRE",
            r"\b(electricidad y magnetismo|dispositivos electronicos|ingenieria de software|estructuras? de datos|sistemas operativos|bases de datos|lenguajes formales y automatas|senales y sistemas|fundamentos de programacion|algebra)\b",
        ),
        ("SALUDO", r"\b(hola|buenas?|que tal)\b"),
        ("DESPEDIDA", r"\b(adios|salir|chao|bye)\b"),
        ("SKIP", r"[,\.\?\!\s]+"),
        ("MISC", r"."),
    ]

    # Inicializar lexer y memoria de contexto del usuario
    lexer = Lexer(reglas)
    continuar_chat = True
    contexto = {"semestre_actual": None, "materia_actual": None}

    print("==================================================")
    print("  Asistente Académico FI-UNAM (Plan 2023)")
    print("==================================================")

    # Captura de la consulta inicial
    entrada_usuario = input(
        "\nHola, soy tu asistente para escoger materias, ¿en qué te puedo ayudar?\nUsuario > "
    )

    # Ciclo principal del bot (REPL)
    while continuar_chat:
        texto_limpio = entrada_usuario.lower().strip()
        tokens = lexer.tokenizar(texto_limpio)

        # Evaluar token de salida
        if any(t.tipo == "DESPEDIDA" for t in tokens):
            continuar_chat = False
            break

        # Análisis semántico de los tokens generados
        intenciones, clave, materia_nombre, semestre = analizador_semantico(tokens)

        # Verificar si la consulta incluye información suficiente o hay contexto previo
        consulta_valida = bool(
            clave
            or materia_nombre
            or semestre
            or intenciones
            or contexto["semestre_actual"]
        )

        if consulta_valida:
            respuesta = consultar_y_responder(
                intenciones, clave, materia_nombre, semestre, texto_limpio, contexto
            )
            print(f"\n[IA]:\n{respuesta}\n")
        else:
            print("\n[IA]: Lo siento, no logré entender tu consulta.")
            print(
                "     Indica la clave (ej: 1539), el nombre de la materia o el semestre que deseas consultar.\n"
            )

        # Solicitar siguiente consulta al usuario
        entrada_usuario = input("Usuario > ")

    print("\n[IA]: Sesión finalizada. ¡Hasta luego!")


if __name__ == "__main__":
    main()
