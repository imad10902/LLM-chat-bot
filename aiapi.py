import openai
import config

api_key= config.DevelopmentConfig.OPENAI_KEY
openai.api_key= api_key

def generateChatResponse(messages):

    response= openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)

    answer= response['choices'][0]['message']['content'].replace('\n', '<br>')
    return answer