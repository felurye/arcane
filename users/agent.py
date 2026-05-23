from pathlib import Path
from abc import abstractmethod
import datetime

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
from tzlocal import get_localzone_name

from prompts.prompt import SUMMARY_PROMPT, EXAM_ANALYSIS_PROMPT
from .tools import buscar_eventos_adversos_veterinarios

load_dotenv()

SKILLS_DIR = Path(__file__).parent / "skills"


# --- Triage Agent ---

class TriagemResponse(BaseModel):
    cor: str = Field(description="A cor da triagem: verde, amarelo, laranja, vermelho")


class TriagemAgent:

    @classmethod
    def build_agent(cls):
        return Agent(
            name="TriagemAgent",
            model=OpenAIResponses(id="gpt-4o-mini"),
            description=(
                "Realiza a triagem de um paciente com base nos dados de entrada; "
                "use a skill triagem para realizar a triagem."
            ),
            instructions=["Use a skill triagem-veterinaria para realizar a triagem."],
            output_schema=TriagemResponse,
            skills=Skills(loaders=[LocalSkills(str(SKILLS_DIR))]),
        )

    @classmethod
    def mount_prompt(cls, frequencia_cardiaca, frequencia_respiratoria, temperatura, peso, queixa, observacao):
        return f"""
            Frequencia Cardiaca: {frequencia_cardiaca} bpm
            Frequencia Respiratoria: {frequencia_respiratoria} mpm
            Temperatura: {temperatura} °C
            Peso: {peso} kg
            Queixa: {queixa}
            Observacao: {observacao}
        """


# --- Summary and Exam Analysis Agents ---

class Summaries(BaseModel):
    summaries: str = Field(description='Resumo')


class ExamAnalyses(BaseModel):
    analyses: list[str] = Field(description='Lista de análises')


class BaseAgent:
    llm = ChatOpenAI(model_name='gpt-4o-mini', openai_api_key=settings.OPENAI_API_KEY)
    language: str = 'pt-br'
    audience: str = 'Veterinario'

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
    VECTOR_DB_TABLE = "documentos"
    VECTOR_DB_URI = "lancedb"
    MEMORY_DB_FILE = "db.sqlite3"
    MEMORY_TABLE = "my_memory_table"
    AGENT_NAME = "Assistente Veterinario Virtual"
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
    - Sempre que solicitado informacoes sobre medicamentos ou principios ativos, use a tools buscar_eventos_adversos_veterinarios para consultar no FDA.
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
    def build_agent(cls, knowledge_filters: dict = {}, session_id: int = 0) -> Agent:
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
            tools=[buscar_eventos_adversos_veterinarios],
            update_memory_on_run=True,
            knowledge=cls.knowledge,
            knowledge_filters=knowledge_filters,
            search_knowledge=True,
            session_id=session_id,
        )


# --- Secretary Agent (WhatsApp) ---

class SecretariaAI:
    CREDENTIALS_PATH = settings.BASE_DIR / "client_secret_850364294536-n0snuu77gar2k1reh738vfa2p5jqv7nd.apps.googleusercontent.com.json"
    VECTOR_DB_TABLE = "empresa"
    VECTOR_DB_URI = "lancedb"
    MEMORY_DB_FILE = "db.sqlite3"
    MEMORY_TABLE = "secretaria_memory_table"

    INSTRUCTIONS = f"""
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

    Data e hora atual: {datetime.datetime.now()}
    Fuso horário: {get_localzone_name()}
    """

    @classmethod
    def build_agent(cls, knowledge_filters: dict = {}, session_id: int = 1) -> Agent:
        db = SqliteDb(
            db_file=cls.MEMORY_DB_FILE,
            memory_table=cls.MEMORY_TABLE
        )

        return Agent(
            name="Assistente de Secretaria Virtual",
            description="Assistente virtual para atendimento ao cliente e agendamento de reuniões",
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
