# Asistente Académico FI-UNAM (Plan 2023)

## Lugar y fecha
* **Lugar:** Facultad de Ingeniería, Universidad Nacional Autónoma de México (UNAM), Ciudad de México.
* **Fecha:** 18 Septiembre de 2026

---

## Integrantes del equipo
* **Alumno 1:** Martinez Ojeda Jonhatan Alexis
* **Alumno 2:** Chavez Garcia Isaac
* **Alumno 3:** Soto Orozco Manuel Minoru
* **Alumno 4:** Garrido Eniquez Omar
* **Alumno 5:** Hernandez Irineo Jorge Manuel

---

## Requisitos

### Lenguaje y Versión
* **Python:** Versión 3.10 o superior.

### Dependencias
El proyecto utiliza exclusivamente la biblioteca estándar de Python, por lo que **no se requiere instalar bibliotecas externas** mediante `pip`. Los módulos internos empleados son:
* `re` — Procesamiento y coincidencia de expresiones regulares (Analizador Léxico).
* `json` — Carga y decodificación de la base de datos de asignaturas por semestre.
* `pathlib` — Gestión dinámica y orientada a objetos de rutas relativas dentro del repositorio.

---

## Instrucciones de instalación y uso

### 1. Clonar el repositorio
Abre una terminal y clona el proyecto en tu equipo local:
```bash
git clone [https://github.com/IngIsaacCG/IAPractica01](https://github.com/IngIsaacCG/IAPractica01)

### Estructura de archivos
IAPractica01/
├── json/
│   ├── primersemestre.json
│   ├── segundosemestre.json
│   ├── ...
│   └── octavosemestre.json
└── src/
    └── practica01.py

### Ejecicion del programa
python src/practica01.py