# mental_health_chain.py
from langchain.chains import ConversationChain
# from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
# from langchain_community.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

def create_mental_health_chain(openai_api_key: str, temperature=0.5):
    """
    创建用于心理健康对话的 LangChain 对象。
    采用 ConversationChain + Memory 的模式。
    """
    # 这里使用对话式模型 (ChatOpenAI)，若需要GPT-3文本模型可改用OpenAI(...)
    chat_model = ChatOpenAI(
        openai_api_key=openai_api_key,
        temperature=temperature
    )

    # 对话内存，用于多轮交互
    memory = ConversationBufferMemory(return_messages=True)

    # 构造对话链
    conversation_chain = ConversationChain(
        llm=chat_model,
        memory=memory,
        verbose=True
    )
    return conversation_chain


def create_mental_health_chain_with_prompt(openai_api_key: str, temperature=0.5):
    chat_model = ChatOpenAI(
        openai_api_key=openai_api_key,
        temperature=temperature
    )
    memory = ConversationBufferMemory(return_messages=True)

    system_template = """\
你是一名心理健康咨询师，擅长倾听、共情，并能给出适度建议。
对话背景：你需要温和且专业地与用户对话，帮助用户缓解压力或焦虑。
    """

    user_template = """\
用户说：{input}
    """

    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    user_message_prompt = HumanMessagePromptTemplate.from_template(user_template)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, user_message_prompt])

    # 通过 LLMChain 将提示模板和模型连接
    chain = LLMChain(
        llm=chat_model,
        prompt=chat_prompt,
        memory=memory,
        verbose=True
    )
    return chain