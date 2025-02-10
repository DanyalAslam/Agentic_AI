# "Programmatic agent hand-off" refers to the scenario where multiple agents are called in succession,
# agents are independent and can be used in any order, and the output of one agent is used as input for another agent.

# Here we show two agents used in succession, the first to find a flight and the second to extract the user's seat preference.

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..')) # Targets to the src directory of the project

from typing import Dict, List, Optional,Union
import nest_asyncio
from pydantic import BaseModel, Field
from pydantic_ai import Agent, ModelRetry, RunContext, Tool
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.models.openai import OpenAIModel
import json
import random
from rich.prompt import Prompt
from pydantic_ai.messages import ModelMessage
from pydantic_ai.usage import Usage, UsageLimits
from Models.models import FlightDetails
from Models.models import Failed
from Api_Keys import api_key_openAI, api_key_groq


model_Llama_33_70B = GroqModel('llama-3.3-70b-versatile',api_key=api_key_groq)
model_OpenAI_35_turbo = OpenAIModel('gpt-3.5-turbo-1106', api_key=api_key_openAI)



import asyncio

#defining the first agent (Search flight agent)
flight_search_agent = Agent[None, Union[FlightDetails, Failed]](
    model=model_Llama_33_70B,
     result_type=Union[FlightDetails, Failed],
       system_prompt=(
        'Use the "flight_search" tool to find a flight '
        'from the given origin to the given destination.'
    ),
    )


async def find_flight() -> str:
    for _ in range(3):
        prompt = Prompt.ask('where would you like to fly from and to?')
        result = await flight_search_agent.run(
            prompt,
            usage_limits=UsageLimits(request_limit=5, total_tokens_limit=300),
        )
        if isinstance(result.data, FlightDetails):
            return result.data


async def main():
    print("Programmatic agent hand-off")
    opt_flight_details = await find_flight()



asyncio.run(main())
