import os
from dotenv import load_dotenv
import dspy

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

turbo = dspy.OpenAI(model='gpt-3.5-turbo-instruct', max_tokens=250, api_key=OPENAI_API_KEY)
dspy.settings.configure(lm=turbo)

def docstring_parameter(*sub):
    def dec(obj):
        obj.__doc__ = obj.__doc__.format(*sub)
        return obj
    return dec