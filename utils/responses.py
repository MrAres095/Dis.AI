import os
import openai
import discord
from config import OPENAI_API_KEY
import openai_async

openai.api_key = OPENAI_API_KEY


async def get_response(cb, message):
    try:
        errors = await get_moderation(message.content) # check for moderation
    except Exception as e:
        print("Moderation error")
        print(e)
    errors = False # delete later
    if errors:
        del cb.context[-1]
        return (message, -1)
    
    # build the messages
    while (len(cb.context) > cb.max_message_history_length): # trim cb.context (excluding prompt) if it's >= mmhl
        del cb.context[1:3]
        
    if (cb.prompt_reminder_interval > 0 and len(cb.context) >= cb.prompt_reminder_interval): # insert system message if it didn't occur in the last cb.prompt_reminder_interval messages
        for msg in cb.context[(-1 * cb.prompt_reminder_interval):]:
            if msg['role'] == 'system':
                break
        else:
            cb.context.append({'role':'system', 'content': cb.prompt})

    if cb.context[0]['role'] != 'system':
        cb.context.insert(0, {'role':'system', 'content':cb.prompt})
    
    
    print(f"Context below. (Len: {len(cb.context)})")
    for line in cb.context:
        print(line)
    try:
        completion = await openai_async.chat_complete(
            OPENAI_API_KEY,
            timeout=15,
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
    except Exception as e:
        print(e)
        del cb.context[-1]
        return (message, -2)
    cb.context.append({'role':'assistant', 'content':completion.json()['choices'][0]['message']['content']})
    return message, completion.json()['choices'][0]


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
    response = openai.Moderation.create(input=question)
    if response.results[0].flagged:
        # get the categories that are flagged and generate a message
        result = [
            error
            for category, error in errors.items()
            if response.results[0].categories[category]
        ]
        return result
    return None

