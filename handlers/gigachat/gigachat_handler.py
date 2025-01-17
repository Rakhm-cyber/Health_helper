from langchain_gigachat import GigaChat
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from aiogram import Router, F
from aiogram.types import Message

import utils.config as config

cfg = config.load()

chat = GigaChat(
    credentials=cfg.gigachat_key,
    model='GigaChat:latest',
    verify_ssl_certs=False
)

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Ты - очень квалифицированный специалист в сфере здоровья. Тебя знает весь мир, и ты знаешь,
что можно посоветовать любому человеку для поддержки его здоровья и физического состояния. У тебя всегда 
хорошее настроение. Каждый твой ответ на любой вопрос должен как-то переходить в тематику здорового образа жизни""",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

def call_model(state: MessagesState):
    prompt = prompt_template.invoke(state)
    response = chat.invoke(prompt)
    return {"messages": response}

workflow = StateGraph(state_schema=MessagesState)
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

app = workflow.compile(checkpointer=MemorySaver())

gigachat_router = Router()

@gigachat_router.message(~F.text.startswith("/"))
async def handle_chat_message(message: Message):
    user_id = message.from_user.id
    prompt = message.text
    config = {"configurable": {"thread_id": user_id}}
    input_messages = [HumanMessage(content=prompt)]
    output = await app.ainvoke({"messages": input_messages}, config)
    response = output["messages"][-1].content
    await message.answer(response)

