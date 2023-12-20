from dotenv import load_dotenv
import os

from openai import OpenAI
from langchain.llms import OpenAI as openai
from langchain.chains import RetrievalQA

from lib.utils import getDataChunks, createKnowledgeHub

ResponsePrompt = """Consider you are a legal advisor based in India. Your day to day job is to reply to legal queries in the most simplified language possible by using least words. Make sure the reader of the response might not understand legal jargons so avoid difficult language. You can mention laws, acts, sections, subsections applicable in your response for the sake of reference or to support the accuraccy of your response. At the end of the response also mention the punishments given in the laws for the action if any (optional).

Answer the question using the given knowledge hub as a part of the retriver. Do not answer the question if you think you are unsure about the answer, just reply with "I am not sure about this". Reply in the language of the question, If the question is in hindi reply in hindi, if the question is in bengali reply in bengali and if the question is in english reply in english. use proper law, acts, sections, subsections while responding in hindi.

"""

ActPrompt = """Based on the below text can you give related name of law, act, section, subsection assosciated with it in context with the indian judicial system. get me the response strictly in 2 - 3 words. do not format the response in a list or any other format. just give me the response in plain text. Do not add any sections, subsections or specific laws. Always give response in english.


"""

KYRPromt = """Based on the given data about the user such as age, gender, city, state and profession can you give me the list of 10 specific rights that person must know in his profession, make the rights gender & age specific as well. Make each right a sentence and do not add any other information such as laws, acts, sections, subsections or punishments. Do not format the response in a list or any other format. Just give me the rights in plain text where each right is separated by a new line.

Person: """

SpecsPromt = """Depending upon the given question what are the different specifications the given question can be categorized into. The options are ["Criminal Law", "Civil Law", "Common Law", "Statutory Law", "Cyber Law"]. You can return multiple options if the question can be categorized into multiple categories. Return the response in comma separated values. do not add any thing else in the response.

"""

client = OpenAI(api_key=os.getenv("OPENAI_KEY"), organization=os.getenv("ORG"))

def generateResponse(text, question):
    chunks = getDataChunks(text)
    knowledge_hub = createKnowledgeHub(chunks)
    retriever = knowledge_hub.as_retriever(search_type="similarity", search_kwargs={"k": 2})
    
    chain = RetrievalQA.from_chain_type(
        llm=openai(api_key=os.getenv("OPENAI_KEY"), organization=os.getenv("ORG"), temperature=0.6, model_name="gpt-3.5-turbo-instruct", max_tokens=600),
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
    )
    
    result = chain({"query": ResponsePrompt + "Question: " + question})
    print(result)
    return result['result']

def regenerateResponse(text, question, response):
    chunks = getDataChunks(text)
    knowledge_hub = createKnowledgeHub(chunks)
    retriever = knowledge_hub.as_retriever(search_type="similarity", search_kwargs={"k": 2})
    
    chain = RetrievalQA.from_chain_type(
        llm=openai(api_key=os.getenv("OPENAI_KEY"), organization=os.getenv("ORG"), temperature=0.6, model_name="gpt-3.5-turbo-instruct", max_tokens=600),
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
    )
    
    result = chain({"query": ResponsePrompt + "Question: " + question + "\n\nThe user is not satisfied with your previous answer\nPrevious Answer: " + response + "\nPlease provide a better answer."})
    return result['result']

def generateChatResponse(text, previousContext, followUpQuestion):
    chunks = getDataChunks(text)
    knowledge_hub = createKnowledgeHub(chunks)
    retriever = knowledge_hub.as_retriever(search_type="similarity", search_kwargs={"k": 2})
    
    chain = RetrievalQA.from_chain_type(
        llm=openai(api_key=os.getenv("OPENAI_KEY"), organization=os.getenv("ORG"), temperature=0.6, model_name="gpt-3.5-turbo-instruct", max_tokens=600),
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
    )
    
    result = chain({"query": ResponsePrompt + "Previous Context: " + previousContext + "\n\nQuestion: " + followUpQuestion})
    return result['result']

def getAct(question):    
    response = client.completions.create(
      model = "gpt-3.5-turbo-instruct",
      prompt = ActPrompt + question,
      max_tokens=50,
    )
    return response.choices[0].text

def getSpecs(question):    
    response = client.completions.create(
      model = "gpt-3.5-turbo-instruct",
      prompt = SpecsPromt + question,
      max_tokens=50,
    )
    values = response.choices[0].text
    values = values.split(",")
    values = [value.strip() for value in values]
    values = [value.replace('"', '') for value in values]
    options = ["Criminal Law", "Civil Law", "Common Law", "Statutory Law", "Cyber Law"]
    values = [value for value in values if value in options]
    return values


def getKYR(data):    
    response = client.completions.create(
      model = "gpt-3.5-turbo-instruct",
      prompt = KYRPromt + data,
      max_tokens=500,
    )
    return response.choices[0].text

def visionOCR(imgs):
    msg = [
        {
        "role": "user",
        "content": [
            {"type": "text", "text": "Detect the language and return the exact text from the image."},
        ],
        }
    ]
    
    for img in imgs:
        msg[0]['content'].append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{img}",
            },
        })
    
    response = client.chat.completions.create(
    model="gpt-4-vision-preview",
    messages=msg,
    max_tokens=300,
    )

    return response.choices[0].message.content

def SummarizeLegalText(text, lang):
    print(lang)
    prompt = f"Summarize the provided legal text using straightforward language, ensuring retention of all essential legal details. If the document refers to any acts, laws, or sections within the Indian judicial system, explicitly mention them and provide clear explanations in simplified terms. Maintain the approach of preserving crucial legal information while simplifying complex language. Do not introduce any extraneous details or information.\n\n{text}\n\nPlease respond with the appropriate summary strictly in {lang}"
    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=2000,
    )
    return response.choices[0].text