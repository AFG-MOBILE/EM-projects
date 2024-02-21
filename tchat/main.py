from langchain_openai.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import HumanMessagePromptTemplate, ChatMessagePromptTemplate
from dotenv import load_dotenv

load_dotenv()

chat = ChatOpenAI()

prompt = ChatMessagePromptTemplate(
    input_variables = ["content"],
    messages=[
        HumanMessagePromptTemplate.from_template("{content}")
    ]
)

chain = LLMChain(
    llm=chat,
    prompt=prompt
)

while True:
    content = input(">> ")
    result = chain({"content":content})
    print(result["text"])