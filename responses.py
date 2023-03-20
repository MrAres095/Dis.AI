import os
import openai
from colorama import Fore, Back, Style
import discord
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


async def get_response(cb, message):
    print("started getting response)")
    errors = await get_moderation(message.content) # check for moderation
    errors = False
    if errors:
        del cb.context[-1]
        return (message, -1)
    # build the messages
    if (len(cb.context) >= cb.max_message_history_length):
        del cb.context[1]
        
    if (cb.prompt_reminder_interval > 0 and len(cb.context) >= cb.prompt_reminder_interval):
        for msg in cb.context[(-1 * cb.prompt_reminder_interval):]:
            if msg['role'] == 'system':
                break
        else:
            cb.context.append({'role':'system', 'content': cb.prompt})

    if cb.context[0]['role'] != 'system':
        cb.context.insert(0, {'role':'system', 'content':cb.prompt})
        
    print(f"Length of send message: {len(cb.context)}")
    print(cb.context)
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=cb.context,
            max_tokens=cb.max_tokens,
            temperature=cb.temperature,
            top_p=cb.top_p,
            n=cb.n,
            presence_penalty=cb.presence_penalty,
            frequency_penalty=cb.frequency_penalty
        )
    except Exception as e:
        print(e)
    print("got completion")
    cb.context.append({'role':'assistant', 'content':completion.choices[0].message.content})
    return message, completion.choices[0]


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


def main():
    os.system("cls" if os.name == "nt" else "clear")
    # keep track of previous questions and answers
    previous_questions_and_answers = []
    while True:
        # ask the user for their question
        new_question = input(
            Fore.GREEN + Style.BRIGHT + "What can I get you?: " + Style.RESET_ALL
        )
        # check the question is safe
        errors = get_moderation(new_question)
        if errors:
            print(
                Fore.RED
                + Style.BRIGHT
                + "Sorry, you're question didn't pass the moderation check:"
            )
            for error in errors:
                print(error)
            print(Style.RESET_ALL)
            continue
        response = get_response(INSTRUCTIONS, previous_questions_and_answers, new_question)

        # add the new question and answer to the list of previous questions and answers
        previous_questions_and_answers.append((new_question, response))

        # print the response
        print(Fore.CYAN + Style.BRIGHT + "Here you go: " + Style.NORMAL + response)


if __name__ == "__main__":
    main()
