# -*- coding: utf-8 -*-
"""Eu Tenho Direito? Assistente Jurídico - Projeto Imersão Alura

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1XHumG00nfiQNj6THESWlmqUSFbUqUGdJ
"""

!pip install -q google-adk

import os
from google.colab import userdata

os.environ["GOOGLE_API_KEY"] = userdata.get('GOOGLE_API_KEY')

from google import genai

client = genai.Client()

MODEL_ID = "gemini-2.0-flash"

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types  # Para criar conteúdos (Content e Part)
from datetime import date
import textwrap # Para formatar melhor a saída de texto
from IPython.display import display, Markdown # Para exibir texto formatado no Colab
import requests # Para fazer requisições HTTP
import warnings

warnings.filterwarnings("ignore")

def call_agent(agent: Agent, message_text: str) -> str:

    session_service = InMemorySessionService()

    session = session_service.create_session(app_name=agent.name, user_id="user1", session_id="session1")

    runner = Runner(agent=agent, app_name=agent.name, session_service=session_service)

    content = types.Content(role="user", parts=[types.Part(text=message_text)])

    final_response = ""

    for event in runner.run(user_id="user1", session_id="session1", new_message=content):
        if event.is_final_response():
          for part in event.content.parts:
            if part.text is not None:
              final_response += part.text
              final_response += "\n"
    return final_response

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

def agente_pesquisador(topico, data_de_hoje):

   pesquisador = Agent(
        name="agente_pesquisador",
        model="gemini-2.0-flash",
        instruction="""
        Você é um assistente pessoal. Sua tarefa é pesquisar o caso do usuário no Google (google_search) e retornar os resultados, informando se o usuário tem direito possui aquele direito ou não.
        Utilize linguagem simples e objetiva. Baseie seu resultado em jurisprudência atual. Seja breve. Não faça novas perguntas.
        """,
        description="Agente que busca informações no Google",
        tools=[google_search]
    )

   entrada_do_agente_pesquisador = f"Tópico: {topico}\nData de hoje: {data_de_hoje}"

   lancamentos = call_agent(pesquisador, entrada_do_agente_pesquisador)
   return lancamentos

def agente_informativo(topico, lancamentos_buscados):
    informativo = Agent(
        name="agente_informativo",
        model="gemini-2.0-flash",
        instruction="""
        Você é um assistente informativo. Sua tarefa é analisar as respostas do agente_pesquisador e determinar se o usuário precisa de um advogado ou pode ser atendido através do Juizado Especial Cível.
        Você deve utilizar a busca do Google (google_search) para tomar sua decisão. Apresente ao usuário somente a opção que melhor se aplicar ao caso. Casos da área trabalhista, previdenciário e criminal sempre precisam de advogado.
        Casos que pareçam ser de menor complexidade ou com valores inferiores a 20 salários mínimos não precisam de advogado.
        """,
        description="Agente que informa",
        tools=[google_search]
    )

    entrada_do_agente_informativo = f"Tópico:{topico}\nLançamentos buscados: {lancamentos_buscados}"
    # Executa o agente
    onde_ir = call_agent(informativo, entrada_do_agente_informativo)
    return onde_ir

def agente_documentador(topico, lancamentos_buscados):
    documentador = Agent(
        name="agente_documentador",
        model="gemini-2.0-flash",
        instruction=""" Você é um assistente de documentação. Você deve listar todos os documentos necessários para o caso do usuário. Utilize o Google (google_search) para pesquisar sobre os documentos necessários.
        Utilize linguagem simples e objetiva. Os documentos devem ser apresentados em ordem de lista.
        """,
        description="Agente que cria lista",
        tools = [google_search]
    )
    entrada_do_agente_documentador = f"Tópico: {topico}\nLançamentos: {lancamentos_buscados}"
    # Executa o agente
    documentos_necessarios = call_agent(documentador, entrada_do_agente_documentador)
    return documentos_necessarios

def agente_localizador(cidade):

   localizador = Agent(
        name="agente_localizador",
        model="gemini-2.0-flash",
        instruction="""
        Você é um assistente de endereços. Sua tarefa é pesquisar através do Google (google_search) o endereço do juizado especial cível e a defensoria pública mais próxima para a cidade do usuário.
        """,
        description="Agente que busca endereços no Google",
        tools=[google_search]
    )

   entrada_do_agente_localizador = f"Tópico: {cidade}"
   return call_agent(localizador, entrada_do_agente_localizador)

data_de_hoje = date.today().strftime("%d/%m/%Y")

print("Olá, Estou aqui para o direito para você e ainda te orientar sobre o que fazer!")

topico = input("Me conte o seu caso: ")

if not topico:
    print("Você esqueceu de me contar seu caso!")
else:
    print(f"Veja como resolver o seu problema: {topico}")

    lancamentos_buscados = agente_pesquisador(topico, data_de_hoje)
    print("\n--- 📝 Resultado do Agente 1 (Pesquisador) ---\n")
    display(to_markdown(lancamentos_buscados))
    print("--------------------------------------------------------------")

    onde_ir = agente_informativo(topico, lancamentos_buscados)
    print("\n--- 📝 Resultado do Agente 2 (Informativo) ---\n")
    display(to_markdown(onde_ir))
    print("--------------------------------------------------------------")

    lista = agente_documentador(topico, lancamentos_buscados)
    print("\n--- 📝 Resultado do Agente 3 (Redator) ---\n")
    display(to_markdown(lista))
    print("--------------------------------------------------------------")


continuação = input("Você gostaria de saber o endereço da defensoria pública ou juizado especial? ")

if continuação.lower() == "sim":
    cidade = input("Digite a sua cidade e estado: ")

    enderecos = agente_localizador(cidade)
    print("\n--- 📝 Resultado do Agente 4 (Localizador) ---\n")
    display(to_markdown(enderecos))
    print("--------------------------------------------------------------")

else:
    print(f"Que bom que pude ajudar. Até a próxima!")