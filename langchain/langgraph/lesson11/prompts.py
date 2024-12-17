from dotenv import load_dotenv, find_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama.chat_models import ChatOllama
from langchain_openai import ChatOpenAI

_ = load_dotenv(find_dotenv())
# 定义写作提示模板
writer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a writing assistant tasked with creating well-crafted, coherent, and engaging articles based on the user's request."
            " Focus on clarity, structure, and quality to produce the best possible piece of writing."
            " If the user provides feedback or suggestions, revise and improve the writing to better align with their expectations.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

# 定义反思提示模板
reflection_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a teacher grading an article submission. Provide critique and recommendations for the user's submission."
            " Include detailed recommendations, such as length, depth, style, etc.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)
research_llm = ChatOpenAI(model="gpt-4o-mini", max_tokens=10000, temperature=0.5)
# 初始化写作模型
writer = writer_prompt | research_llm

# 初始化反思模型
reflect = reflection_prompt | research_llm
# writer = writer_prompt | ChatOllama(
#     model="llama3.1:8b-instruct-q8_0",
#     max_tokens=8192,
#     temperature=1.2,
# )
#
# # 初始化反思模型
# reflect = reflection_prompt | ChatOllama(
#     model="llama3.1:8b-instruct-q8_0",
#     max_tokens=8192,
#     temperature=0.2,
# )
