from pathlib import Path
from abc import abstractmethod
import httpx
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIResponses, OpenAIChat
from agno.skills import LocalSkills, Skills
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.lancedb import LanceDb
from agno.db.sqlite import SqliteDb
from agno.tools.googlecalendar import GoogleCalendarTools
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from django.conf import settings

from prompts.prompt import SUMMARY_PROMPT, EXAM_ANALYSIS_PROMPT
from .tools import search_adverse_veterinary_events

load_dotenv()

SKILLS_DIR = Path(__file__).parent / "skills"


# --- Triage Agent ---

class TriageResponse(BaseModel):
    color: str = Field(description="Triage color: green, yellow, orange, red")


class TriageAgent:

    @classmethod
    def build_agent(cls):
        return Agent(
            name="TriageAgent",
            model=OpenAIResponses(id="gpt-4o-mini"),
            description=(
                "Realiza a triagem de um paciente com base nos dados de entrada; "
                "use a skill triagem para realizar a triagem."
            ),
            instructions=["Use a skill veterinary-triage para realizar a triagem."],
            output_schema=TriageResponse,
            skills=Skills(loaders=[LocalSkills(str(SKILLS_DIR))]),
        )

    @classmethod
    def mount_prompt(cls, heart_rate, respiratory_rate, temperature, weight, complaint, observation):
        return f"""
            Frequencia Cardiaca: {heart_rate} bpm
            Frequencia Respiratoria: {respiratory_rate} mpm
            Temperatura: {temperature} °C
            Peso: {weight} kg
            Queixa: {complaint}
            Observacao: {observation}
        """


# --- Summary and Exam Analysis Agents ---

class Summaries(BaseModel):
    summaries: str = Field(description='Summary')


class ExamAnalyses(BaseModel):
    analyses: list[str] = Field(description='List of analyses')


class BaseAgent:
    llm = ChatOpenAI(model_name='gpt-4o-mini', openai_api_key=settings.OPENAI_API_KEY)
    language: str = 'pt-br'
    audience: str = 'Veterinarian'

    @abstractmethod
    def _prompt(self): ...

    @abstractmethod
    def run(self): ...


class SummaryAgent(BaseAgent):
    def _prompt(self):
        return ChatPromptTemplate.from_messages([
            ('system', SUMMARY_PROMPT),
            ('human', 'language: {language} | audience: {audience}\nUse a transcrição abaixo: {transcription}'),
        ])

    def run(self, transcription):
        chain = self._prompt() | self.llm.with_structured_output(Summaries)
        return chain.invoke({'transcription': transcription, 'language': self.language, 'audience': self.audience})


class ExamAnalysisAgent(BaseAgent):
    def _prompt(self):
        return ChatPromptTemplate.from_messages([
            ('system', EXAM_ANALYSIS_PROMPT),
            ('human', 'language: {language} | audience: {audience}\nExames: {exam_results}'),
        ])

    def run(self, exam_results):
        chain = self._prompt() | self.llm.with_structured_output(ExamAnalyses)
        return chain.invoke({'exam_results': exam_results, 'language': self.language, 'audience': self.audience})


# --- Assistant Agent (RAG) ---

class AssistantAgent:
    VECTOR_DB_TABLE = "documents"
    VECTOR_DB_URI = "lancedb"
    MEMORY_DB_FILE = "db.sqlite3"
    MEMORY_TABLE = "my_memory_table"
    AGENT_NAME = "Virtual Veterinary Assistant"
    AGENT_DESCRIPTION = (
        "Assistente virtual especializado em consultas veterinarias "
        "use a base de conhecimento de consultas veterinarias"
    )
    INSTRUCTIONS = """
    SUAS CAPACIDADES:
    1. Acesso a Base de Conhecimento (RAG): Você possui acesso a uma base de dados
       e deve usá-la para responder as perguntas do usuário de forma precisa e fundamentada.
    2. Consulta de Medicamentos: Você pode buscar informações sobre medicamentos
       através da API do FDA.

    DIRETRIZES:
    - Sempre priorize informações da base de conhecimento quando disponíveis.
    - Ao consultar medicamentos, forneça informações claras e organizadas.
    - Se não tiver certeza sobre alguma informação, indique isso ao usuário.
    - Mantenha um tom profissional e objetivo em todas as respostas.
    - Sempre devolva a resposta em markdown
    - Sempre que solicitado informacoes sobre medicamentos ou principios ativos, use a tool search_adverse_veterinary_events para consultar no FDA.
    - Quando buscar informacoes sobre medicamentos ou principios ativos, nunca devolva a resposta da API traga a sua interpretacao dos dados com o contexto da pergunta.
    """

    knowledge = Knowledge(
        vector_db=LanceDb(
            table_name=VECTOR_DB_TABLE,
            uri=VECTOR_DB_URI,
            embedder=OpenAIEmbedder()
        ),
    )

    @classmethod
    def build_agent(cls, knowledge_filters: dict | None = None, session_id: int = 0) -> Agent:
        knowledge_filters = knowledge_filters or {}
        db = SqliteDb(
            db_file=cls.MEMORY_DB_FILE,
            memory_table=cls.MEMORY_TABLE
        )

        return Agent(
            model=OpenAIResponses(id="gpt-4o-mini"),
            name=cls.AGENT_NAME,
            description=cls.AGENT_DESCRIPTION,
            instructions=cls.INSTRUCTIONS,
            db=db,
            tools=[search_adverse_veterinary_events],
            update_memory_on_run=True,
            knowledge=cls.knowledge,
            knowledge_filters=knowledge_filters,
            search_knowledge=True,
            session_id=session_id,
        )


# --- Secretary Agent (WhatsApp) ---

class SecretaryAI:
    CREDENTIALS_PATH = settings.BASE_DIR / "client_secret_850364294536-n0snuu77gar2k1reh738vfa2p5jqv7nd.apps.googleusercontent.com.json"
    VECTOR_DB_TABLE = "empresa"
    VECTOR_DB_URI = "lancedb"
    MEMORY_DB_FILE = "db.sqlite3"
    MEMORY_TABLE = "secretary_memory_table"

    INSTRUCTIONS = """
    Você é a secretária virtual de um hospital veterinário. Seu papel é agendar consultas para possíveis pacientes.
    SUAS CAPACIDADES:

    1. ATENDIMENTO AO CLIENTE:
       - Seja cordial, profissional e prestativo em todas as interações.
       - Responda perguntas sobre produtos, serviços, preços e políticas da empresa.
       - Forneça informações claras e objetivas.
       - Se não souber algo, ofereça-se para buscar mais informações ou conectar o cliente com o setor adequado.

    2. AGENDAMENTO DE REUNIÕES:
       - Você tem acesso ao Google Calendar para agendar reuniões.
       - IMPORTANTE: Reuniões devem ser agendadas APENAS entre 11h e 18h (horário local).
       - Antes de agendar, SEMPRE verifique os horários disponíveis no calendário.
       - Procure por espaços livres no calendário entre 11h e 18h.
       - Se o cliente solicitar um horário fora desse intervalo, explique que os agendamentos são apenas entre 13h e 18h e ofereça alternativas dentro desse horário.
       - Ao criar um evento, inclua:
         * Título descritivo da reunião
         * Data e horário (entre 11h e 18h)
         * Duração sugerida (padrão: 1 hora, a menos que o cliente especifique)
         * Descrição com informações relevantes se fornecidas pelo cliente

    DIRETRIZES DE AGENDAMENTO:
    - Horário permitido: 11:00 às 18:00 (horário local)
    - Sempre verifique disponibilidade antes de confirmar
    - Se não houver horário disponível no dia solicitado, ofereça alternativas nos próximos dias
    - Confirme o agendamento com o cliente antes de criar o evento

    FLUXO DE ATENDIMENTO:
    1. Cumprimente o cliente de forma cordial
    2. Identifique a necessidade (informação ou agendamento)
    3. Para informações: consulte a base de conhecimento e responda
    4. Para agendamento: verifique disponibilidade e agende entre 11h-18h
    5. Confirme todas as informações antes de finalizar
    """

    @classmethod
    def build_agent(cls, knowledge_filters: dict | None = None, session_id: int = 1) -> Agent:
        knowledge_filters = knowledge_filters or {}
        db = SqliteDb(
            db_file=cls.MEMORY_DB_FILE,
            memory_table=cls.MEMORY_TABLE
        )

        return Agent(
            name="Virtual Secretary Assistant",
            description="Virtual assistant for client service and appointment scheduling",
            model=OpenAIChat(id="gpt-4o-mini"),
            tools=[GoogleCalendarTools(
                credentials_path=str(cls.CREDENTIALS_PATH),
                allow_update=True
            )],
            instructions=cls.INSTRUCTIONS,
            db=db,
            update_memory_on_run=True,
            session_id=session_id,
            add_history_to_context=True,
            num_history_runs=5,
            add_datetime_to_context=True,
        )
