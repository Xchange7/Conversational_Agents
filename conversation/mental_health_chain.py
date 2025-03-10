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
    Create a LangChain object for mental health conversations.
    Uses the ConversationChain + Memory pattern.
    """
    # Use a conversational model (ChatOpenAI) here. If you need a GPT-3 text model, use OpenAI(...)
    chat_model = ChatOpenAI(
        openai_api_key=openai_api_key,
        temperature=temperature
    )

    # Conversation memory for multi-turn interaction
    memory = ConversationBufferMemory(return_messages=True)

    # Construct the conversation chain
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
You are a mental health consultant, skilled at listening, empathizing, and giving appropriate advice.
Conversation background: You need to talk to the user gently and professionally to help them relieve stress or anxiety.
    """

    user_template = """\
User says: {input}
    """

    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    user_message_prompt = HumanMessagePromptTemplate.from_template(user_template)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, user_message_prompt])

    # Connect the prompt template and model through LLMChain
    chain = LLMChain(
        llm=chat_model,
        prompt=chat_prompt,
        memory=memory,
        verbose=True
    )
    return chain