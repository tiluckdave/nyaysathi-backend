# NyaySathi Backend

This repository contains the backend code for [NyaySathi](https://github.com/tiluckdave/nyaysathi) project. Nyay Sathi is an AI powered platform where people can get legal guidance and advice for their legal quiries through voice input and output in their regional language.

The backend is build using FLask and it is deployed on replit. This flask server is responsible for the following tasks.

1. Handling the incoming requests from the frontend.
2. Using RAG (Retrival Augemented Generation) model with OpenAI's GPT 3 embeddings to generate response for the user's query.
3. Using [Indian Kanoon API](https://www.indiankanoon.org/api/) to fetch relevant legal documents for the user's query to train the RAG model.
4. Using [Narakeet API](https://www.narakeet.com/) to convert the generated response into audio.
5. Sending the response back to the frontend.

## Getting Started

- Setup a virtual environment and install the dependencies.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

- Create a .env file and add the following variables.

```env
OPENAI_API_KEY=<your openai api key>
OPENAI_ORG_ID=<your openai org id>
NARAKEET_API_KEY=<your narakeet api key>
```

- Run the flask server.

```bash
python3 app.py
```

- The server will be running on port 5000.
