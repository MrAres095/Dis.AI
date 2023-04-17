import openai
from EdgeGPT import Chatbot, ConversationStyle
import json
from config import OPENAI_API_KEY, COOKIES
import openai_async
import asyncio
openai.api_key = OPENAI_API_KEY

async def get_bing_response(question, bingbot):
    result = await bingbot.ask(prompt=question, conversation_style=ConversationStyle.creative, wss_link="wss://sydney.bing.com/sydney/ChatHub")
    out = result['item']['messages'][1]['text'] + "\n"
    out += "Sources:\n"
    for url in result['item']['messages'][1]['sourceAttributions']:
            out += "\n" + url['seeMoreUrl']
            
    return out

async def get_response(cb, message, apikey=OPENAI_API_KEY):
    # build the messages
    while (len(cb.context) > cb.max_message_history_length): # trim cb.context (excluding prompt) if it's >= mmhl
        del cb.context[1:3]
        
    if (cb.prompt_reminder_interval > 0 and len(cb.context) >= cb.prompt_reminder_interval): # insert system message if it didn't occur in the last cb.prompt_reminder_interval messages
        for msg in cb.context[(-1 * cb.prompt_reminder_interval):]:
            if msg['role'] == 'system':
                break
        else:
            cb.context.append({'role':'system', 'content': cb.prompt})

    if not cb.context or cb.context[0]['role'] != 'system':
        cb.context.insert(0, {'role':'system', 'content':cb.prompt})
    
    if not apikey:
        apikey=OPENAI_API_KEY
        print(f"Context Len: {len(cb.context)}")
    else:
        print(f"Context Len: {len(cb.context)} - (custom API key)")
    for line in cb.context:
        print(line)
    
    
    
    try:
        completion = await openai_async.chat_complete(
            apikey,
            timeout=300,
            payload={
                "model":"gpt-3.5-turbo",
                "messages":cb.context,
                "max_tokens":cb.max_tokens,
                "temperature":cb.temperature,
                "top_p":cb.top_p,
                "n":cb.n,
                "presence_penalty":cb.presence_penalty,
                "frequency_penalty":cb.frequency_penalty
            }
        )
        if completion.status_code == 401:
            return (-3, "Invalid key")
        cb.context.append({'role':'assistant', 'content':completion.json()['choices'][0]['message']['content']})
        return 0, completion.json()['choices'][0]
    except Exception as e:
        print("responses error")
        print(e)
        del cb.context[-1]
        return (-2, str(e))
    


async def get_moderation(question):
    """
    Check the question is safe to ask the model
    Parameters:
        question (str): The question to check
    Returns a list of errors if the question is not safe, otherwise returns None
    """

    errors = {
        "hate": "Content that expresses, incites, or promotes hate based on race, gender, ethnicity, religion, nationality, sexual orientation, disability status, or caste.",
        "hate/threatening": "Hateful content that also includes violence or serious harm towards the targeted group.",
        "self-harm": "Content that promotes, encourages, or depicts acts of self-harm, such as suicide, cutting, and eating disorders.",
        "sexual": "Content meant to arouse sexual excitement, such as the description of sexual activity, or that promotes sexual services (excluding sex education and wellness).",
        "sexual/minors": "Sexual content that includes an individual who is under 18 years old.",
        "violence": "Content that promotes or glorifies violence or celebrates the suffering or humiliation of others.",
        "violence/graphic": "Violent content that depicts death, violence, or serious physical injury in extreme graphic detail.",
    }
    try:
        response = openai.Moderation.create(input=question)
    except Exception as e:
        return  -1
    if response.results[0].flagged:
        # get the categories that are flagged and generate a message
        result = [
            error
            for category, error in errors.items()
            if response.results[0].categories[category]
        ]
        return result
    return None

