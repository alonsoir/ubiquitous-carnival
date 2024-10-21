import operator
from pydantic import BaseModel, Field
from typing import Annotated, List
from typing_extensions import TypedDict

from langchain_community.document_loaders import WikipediaLoader
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    get_buffer_string,
)
from langchain_openai import ChatOpenAI

from langgraph.constants import Send
from langgraph.graph import END, MessagesState, START, StateGraph
from dotenv import load_dotenv

load_dotenv()
### LLM

llm = ChatOpenAI(model="gpt-4o", temperature=0)


### Esquema


class Analyst(BaseModel):
    afiliación: str = Field(description="Afiliación principal del analista.")
    nombre: str = Field(description="Nombre del analista.")
    rol: str = Field(description="Rol del analista en el contexto del tema.")
    descripción: str = Field(
        description="Descripción del enfoque, preocupaciones y motivos del analista."
    )

    @property
    def persona(self) -> str:
        return f"Nombre: {self.nombre}\nRol: {self.rol}\nAfiliación: {self.afiliación}\nDescripción: {self.descripción}\n"


class Perspectives(BaseModel):
    analistas: List[Analyst] = Field(
        description="Lista completa de analistas con sus roles y afiliaciones."
    )


class GenerateAnalystsState(TypedDict):
    tema: str  # Tema de investigación
    max_analistas: int  # Número de analistas
    comentarios_analista_humano: str  # Comentarios humanos
    analistas: List[Analyst]  # Analista que hace preguntas


class InterviewState(MessagesState):
    max_num_turns: int  # Número máximo de turnos de conversación
    contexto: Annotated[list, operator.add]  # Documentos fuente
    analista: Analyst  # Analista que hace preguntas
    entrevista: str  # Transcripción de la entrevista
    secciones: list  # Clave final para la API Send()


class SearchQuery(BaseModel):
    consulta_busqueda: str = Field(
        None, description="Consulta de búsqueda para recuperación."
    )


class ResearchGraphState(TypedDict):
    tema: str  # Tema de investigación
    max_analistas: int  # Número de analistas
    comentarios_analista_humano: str  # Comentarios humanos
    analistas: List[Analyst]  # Analista que hace preguntas
    secciones: Annotated[list, operator.add]  # Clave API Send()
    introducción: str  # Introducción para el informe final
    contenido: str  # Contenido para el informe final
    conclusión: str  # Conclusión para el informe final
    informe_final: str  # Informe final


### Nodos y bordes

instrucciones_analista = """Tarea: Creación de Personas de Analistas de IA
Revisa el tema de investigación:
{tema}
Examina cualquier comentario editorial que se haya proporcionado opcionalmente para guiar la creación de los analistas:
{comentarios_analista_humano}
Identifica los temas más interesantes basándote en los documentos y/o en los comentarios anteriores.
Selecciona los {max_analistas} temas más relevantes.
Asigna un analista a cada tema seleccionado."""


def create_analysts(state: GenerateAnalystsState):
    """Crear analistas"""

    tema = state["tema"]
    max_analistas = state["max_analistas"]
    comentarios_analista_humano = state.get("comentarios_analista_humano", "")

    structured_llm = llm.with_structured_output(Perspectives)

    system_message = instrucciones_analista.format(
        tema=tema,
        comentarios_analista_humano=comentarios_analista_humano,
        max_analistas=max_analistas,
    )

    analistas = structured_llm.invoke(
        [SystemMessage(content=system_message)]
        + [HumanMessage(content="Genera el conjunto de analistas.")]
    )

    return {"analistas": analistas.analistas}


def human_feedback(state: GenerateAnalystsState):
    """Nodo no operativo que debe ser interrumpido"""
    pass


# Generar pregunta del analista
instrucciones_pregunta = """Tarea: Entrevista a un Experto
Eres un analista encargado de entrevistar a un experto para aprender sobre un tema específico.
Tu objetivo es obtener información interesante y específica relacionada con tu tema.
Interesante: Información que sorprenda o no sea evidente para las personas.
Específico: Información que evite generalidades e incluya ejemplos concretos del experto.
Aquí tienes tu tema de enfoque y conjunto de objetivos: {objetivos}
Comienza presentándote con un nombre que se ajuste a tu persona, y luego formula tu pregunta.
Continúa haciendo preguntas para profundizar y refinar tu comprensión del tema.
Cuando estés satisfecho con tu entendimiento, finaliza la entrevista diciendo: "¡Muchas gracias por tu ayuda!"
Recuerda mantenerte en personaje durante toda tu respuesta, reflejando la persona y los objetivos que se te han proporcionado."""


def generate_question(state: InterviewState):
    """Nodo para generar una pregunta"""

    analista = state["analista"]
    messages = state["messages"]

    system_message = instrucciones_pregunta.format(objetivos=analista.persona)

    question = llm.invoke([SystemMessage(content=system_message)] + messages)

    return {"messages": [question]}


# Escritura de consulta de búsqueda
instrucciones_busqueda = SystemMessage(
    content=f"""Tarea: Generación de Consulta para Búsqueda
Se te proporcionará una conversación entre un analista y un experto.
Tu objetivo es generar una consulta bien estructurada para su uso en recuperación y/o búsqueda web relacionada con la conversación.
Analiza la conversación completa.
Presta especial atención a la última pregunta formulada por el analista.
Convierte esta última pregunta en una consulta de búsqueda web bien estructurada."""
)


def search_web(state: InterviewState):
    """Recuperar documentos de búsqueda web"""

    tavily_search = TavilySearchResults(max_results=3)

    structured_llm = llm.with_structured_output(SearchQuery)
    search_query = structured_llm.invoke([instrucciones_busqueda] + state["messages"])

    search_docs = tavily_search.invoke(search_query.consulta_busqueda)

    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document href="{doc["url"]}"/>\n{doc["content"]}\n</Document>'
            for doc in search_docs
        ]
    )

    return {"contexto": [formatted_search_docs]}


def search_wikipedia(state: InterviewState):
    """Recuperar documentos de Wikipedia"""

    structured_llm = llm.with_structured_output(SearchQuery)
    search_query = structured_llm.invoke([instrucciones_busqueda] + state["messages"])

    search_docs = WikipediaLoader(
        query=search_query.consulta_busqueda, load_max_docs=2
    ).load()

    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}"/>\n{doc.page_content}\n</Document>'
            for doc in search_docs
        ]
    )

    return {"contexto": [formatted_search_docs]}


# Generar respuesta del experto
instrucciones_respuesta = """Tarea: Respuesta de un Experto 
Eres un experto siendo entrevistado por un analista. 
Aquí está el área de enfoque del analista: {objetivos}. 
Tu objetivo es responder a una pregunta planteada por el entrevistador. 
Para responder la pregunta, utiliza el siguiente contexto:
{contexto} 
Al responder las preguntas, sigue estas pautas:
Utiliza únicamente la información proporcionada en el contexto. 
No introduzcas información externa ni hagas suposiciones más allá de lo que se indica explícitamente en el contexto. 
El contexto contiene fuentes al inicio de cada documento individual. 
Incluye estas fuentes en tu respuesta junto a cualquier afirmación relevante. Por ejemplo, para la fuente # 1 utiliza . 
Enumera tus fuentes al final de tu respuesta: Fuente 1, Fuente 2, etc. 
Si la fuente es: <Document source="assistant/docs/llama3_1.pdf" page="7"/>, simplemente enumera:
assistant/docs/llama3_1.pdf, página 7 
Y omite la adición de corchetes así como la introducción "Document source" en tu cita."""


def generate_answer(state: InterviewState):
    """Nodo para responder una pregunta"""

    analista = state["analista"]
    messages = state["messages"]
    contexto = state["contexto"]

    system_message = instrucciones_respuesta.format(
        objetivos=analista.persona, contexto=contexto
    )

    answer = llm.invoke([SystemMessage(content=system_message)] + messages)

    answer.name = "experto"

    return {"messages": [answer]}


def save_interview(state: InterviewState):
    """Guardar entrevistas"""

    messages = state["messages"]

    interview = get_buffer_string(messages)

    return {"entrevista": interview}


def route_messages(state: InterviewState, name: str = "experto"):
    """Ruteo entre pregunta y respuesta"""

    messages = state["messages"]
    max_num_turns = state.get("max_num_turns", 2)

    num_responses = len(
        [m for m in messages if isinstance(m, AIMessage) and m.name == name]
    )

    if num_responses >= max_num_turns:
        return "save_interview"

    last_question = messages[-2]

    if "¡Muchas gracias por tu ayuda!" in last_question.content:
        return "save_interview"

    return "ask_question"


# Escribir un resumen (sección del informe final) de la entrevista
instrucciones_sección_escritura = """Tarea: Redacción Técnica de un Informe 
Eres un experto en redacción técnica. 
Tu tarea es crear una sección breve y fácil de digerir de un informe basada en un conjunto de documentos fuente. 
Analiza el contenido de los documentos fuente:
El nombre de cada documento fuente se encuentra al inicio del documento, con la etiqueta <Document>. 
Crea una estructura del informe utilizando formato markdown:
Usa ## para el título de la sección. 
Usa ### para los encabezados de subsecciones. 

Escribe el informe siguiendo esta estructura:
a. Título (## encabezado)
b. Resumen (### encabezado)
c. Fuentes (### encabezado)

Haz que tu título sea atractivo basado en el área de enfoque del analista:
{foco}

Para la sección de resumen:
Introduce el resumen con un contexto general relacionado con el área de enfoque del analista.
Enfatiza lo que es novedoso, interesante o sorprendente sobre las ideas recopiladas de la entrevista.
Crea una lista numerada de documentos fuente a medida que los utilices.
No menciones los nombres de los entrevistadores ni de los expertos.
Apunta a aproximadamente 400 palabras como máximo.
Utiliza fuentes numeradas en tu informe (por ejemplo, , ) basadas en la información de los documentos fuente.

En la sección de Fuentes:
Incluye todas las fuentes utilizadas en tu informe.
Proporciona enlaces completos a sitios web relevantes o rutas específicas de documentos.
Separa cada fuente por una nueva línea. Usa dos espacios al final de cada línea para crear una nueva línea en Markdown.

Debe verse así:

### Fuentes  
Enlace o nombre del documento  
Enlace o nombre del documento  

Asegúrate de combinar fuentes. Por ejemplo esto no es correcto:

https://ai.meta.com/blog/meta-llama-3-1/  
https://ai.meta.com/blog/meta-llama-3-1/  

No debe haber fuentes redundantes. Debe ser simplemente:

https://ai.meta.com/blog/meta-llama-3-1/  

Revisión final:
Asegúrate que el informe siga la estructura requerida.
No incluyas preámbulo antes del título del informe.
Verifica que se hayan seguido todas las pautas."""


def write_section(state: InterviewState):
    """Nodo para escribir una sección"""

    interview = state["entrevista"]
    contexto = state["contexto"]
    analista = state["analista"]

    system_message = instrucciones_sección_escritura.format(foco=analista.descripción)

    section = llm.invoke(
        [SystemMessage(content=system_message)]
        + [
            HumanMessage(
                content=f"Usa esta fuente para escribir tu sección: {contexto}"
            )
        ]
    )

    return {"secciones": [section.content]}


# Añadir nodos y bordes
interview_builder = StateGraph(InterviewState)
interview_builder.add_node("ask_question", generate_question)
interview_builder.add_node("search_web", search_web)
interview_builder.add_node("search_wikipedia", search_wikipedia)
interview_builder.add_node("answer_question", generate_answer)
interview_builder.add_node("save_interview", save_interview)
interview_builder.add_node("write_section", write_section)

# Flujo
interview_builder.add_edge(START, "ask_question")
interview_builder.add_edge("ask_question", "search_web")
interview_builder.add_edge("ask_question", "search_wikipedia")
interview_builder.add_edge("search_web", "answer_question")
interview_builder.add_edge("search_wikipedia", "answer_question")
interview_builder.add_conditional_edges(
    "answer_question", route_messages, ["ask_question", "save_interview"]
)
interview_builder.add_edge("save_interview", "write_section")
interview_builder.add_edge("write_section", END)


def initiate_all_interviews(state: ResearchGraphState):
    """Borde condicional para iniciar todas las entrevistas a través API Send() o volver a create_analysts"""

    human_analyst_feedback = state.get("comentarios_analista_humano", "approve")
    if human_analyst_feedback.lower() != "approve":
        return "create_analysts"

    else:
        tema = state["tema"]
        return [
            Send(
                "conduct_interview",
                {
                    "analyst": analyst,
                    "messages": [
                        HumanMessage(
                            content=f"Entonces dijiste que estabas escribiendo un artículo sobre {tema}?"
                        )
                    ],
                },
            )
            for analyst in state["analistas"]
        ]


# Escribir un informe basado en las entrevistas
instrucciones_redacción_informe = """Tarea: Redacción de un Informe Técnico  
Eres un redactor técnico creando un informe sobre el siguiente tema general:
{tema}  
Tienes un equipo de analistas. Cada analista ha realizado dos actividades:
Han llevado a cabo una entrevista con un experto sobre un subtema específico.
Han redactado sus hallazgos en un memorando.
Tu tarea:
Se te proporcionará una colección de memorandos de tus analistas.
Piensa detenidamente en los conocimientos de cada memorando.
Consolida estos hallazgos en un resumen claro que integre las ideas centrales de todos los memorandos.
Resume los puntos centrales de cada memorando en una narrativa cohesiva.
Para formatear tu informe:
Utiliza formato markdown.
No incluyas preámbulo en el informe.
No uses subtítulos.
Comienza tu informe con un único encabezado de título: ## Insights  
No menciones nombres de analistas en tu informe.  
Preserva cualquier cita en los memorandos, que estará anotada entre corchetes, por ejemplo, [1] o [2].  
Crea una lista final y consolidada de fuentes y añádela a una sección Fuentes con el encabezado ## Sources.  
Enumera tus fuentes en orden y no repitas ninguna.

### Fuentes  
Enlace o nombre del documento  
Enlace o nombre del documento  

Aquí están los memorandos de tus analistas para construir tu informe:

{contexto}"""


def write_report(state: ResearchGraphState):
    """Nodo para escribir el cuerpo final del informe"""

    secciones_completas = state["secciones"]
    tema = state["tema"]

    formatted_str_sections = "\n\n".join(
        [f"{section}" for section in secciones_completas]
    )

    system_message_informe_finalizado = instrucciones_redacción_informe.format(
        tema=tema, contexto=formatted_str_sections
    )

    report = llm.invoke(
        [SystemMessage(content=system_message_informe_finalizado)]
        + [HumanMessage(content=f"Escribe un informe basado en estos memorandos.")]
    )

    return {"contenido": report.content}


# Escribir introducción o conclusión
intro_conclusion_instructions = """Tarea: Redacción de Introducción o Conclusión  
Eres un redactor técnico finalizando un informe sobre {tema}.  
Se te proporcionarán todas las secciones del informe.  
Tu trabajo es redactar una introducción o una conclusión clara y convincente.   
El usuario te indicará si debes escribir la introducción o la conclusión.   
No incluyas preámbulo en ninguna sección.   
Apunta a alrededor de 100 palabras, presentando concisamente (para introducción) o resumiendo (para conclusión) todas las secciones del informe.   
Utiliza formato markdown.   
Para tu introducción, crea un título atractivo y usa el encabezado # para el título.   
Para tu introducción utiliza ## Introducción como encabezado sección.   
Para tu conclusión utiliza ## Conclusión como encabezado sección.   
Aquí están las secciones donde reflexionarás para escribir:{formatted_str_sections}"""


def write_introduction(state: ResearchGraphState):
    """Nodo para escribir la introducción"""

    sections = state["secciones"]
    topic = state["tema"]

    formatted_str_sections = "\n\n".join([f"{section}" for section in sections])

    instructions = intro_conclusion_instructions.format(
        topic=topic, formatted_str_sections=formatted_str_sections
    )

    introduction = llm.invoke(
        [SystemMessage(content=instructions)]
        + [HumanMessage(content="Escribe una introducción para el informe.")]
    )

    return {"introducción": introduction.content}


def write_conclusion(state: ResearchGraphState):
    """Node to write the conclusion"""

    # Full set of sections
    sections = state["sections"]
    topic = state["topic"]

    # Concat all sections together
    formatted_str_sections = "\n\n".join([f"{section}" for section in sections])

    # Summarize the sections into a final report

    instructions = intro_conclusion_instructions.format(
        topic=topic, formatted_str_sections=formatted_str_sections
    )
    conclusion = llm.invoke(
        [instructions] + [HumanMessage(content=f"Write the report conclusion")]
    )
    return {"conclusion": conclusion.content}


def finalize_report(state: ResearchGraphState):
    """The is the "reduce" step where we gather all the sections, combine them, and reflect on them to write the intro/conclusion"""

    # Save full final report
    content = state["content"]
    if content.startswith("## Insights"):
        content = content.strip("## Insights")
    if "## Sources" in content:
        try:
            content, sources = content.split("\n## Sources\n")
        except:
            sources = None
    else:
        sources = None

    final_report = (
        state["introduction"]
        + "\n\n---\n\n"
        + content
        + "\n\n---\n\n"
        + state["conclusion"]
    )
    if sources is not None:
        final_report += "\n\n## Sources\n" + sources
    return {"final_report": final_report}


# Add nodes and edges
builder = StateGraph(ResearchGraphState)
builder.add_node("create_analysts", create_analysts)
builder.add_node("human_feedback", human_feedback)
builder.add_node("conduct_interview", interview_builder.compile())
builder.add_node("write_report", write_report)
builder.add_node("write_introduction", write_introduction)
builder.add_node("write_conclusion", write_conclusion)
builder.add_node("finalize_report", finalize_report)

# Logic
builder.add_edge(START, "create_analysts")
builder.add_edge("create_analysts", "human_feedback")
builder.add_conditional_edges(
    "human_feedback", initiate_all_interviews, ["create_analysts", "conduct_interview"]
)
builder.add_edge("conduct_interview", "write_report")
builder.add_edge("conduct_interview", "write_introduction")
builder.add_edge("conduct_interview", "write_conclusion")
builder.add_edge(
    ["write_conclusion", "write_report", "write_introduction"], "finalize_report"
)
builder.add_edge("finalize_report", END)

# Compile
graph = builder.compile(interrupt_before=["human_feedback"])
print("grafo compilado")

# Probar el grafo con un input
input_data = {
    "tema": "Retrieval-Augmented Generation (RAG) en Procesamiento de Lenguaje Natural",
    "max_analistas": 3,
    "comentarios_analista_humano": "Buscamos analistas con experiencia en IA y NLP."
}
print(f"Los datos de entrada del grafo son: {input_data}\n")
output = graph.invoke(input_data)
# Imprimir el output de forma legible
print("\nOutput Data:")
for key, value in output.items():
    if isinstance(value, list):
        print(f"{key}:")
        for analyst in value:
            print(f"  - {analyst.nombre} ({analyst.rol}, {analyst.afiliación}): {analyst.descripción}")
    else:
        print(f"{key}: {value}")

# Si hay secciones, imprimirlas también
if 'secciones' in output and output['secciones']:
    print("\nSecciones:")
    for section in output['secciones']:
        print(f"  - {section}")