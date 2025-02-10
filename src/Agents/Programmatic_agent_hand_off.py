# "Programmatic agent hand-off" refers to the scenario where multiple agents are called in succession,
# agents are independent and can be used in any order, and the output of one agent is used as input for another agent.

# Here we show two agents used in succession, the first to find a flight and the second to extract the user's seat preference.

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..')) # Targets to the src directory of the project

from typing import Union
import asyncio
from pydantic_ai import Agent,RunContext, Tool
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.usage import Usage
from rich.prompt import Prompt
from pydantic_ai.messages import ModelMessage
from pydantic_ai.usage import Usage
from Models.models import FlightDetails, Failed, SeatPreference
from Api_Keys import api_key_openAI, api_key_groq


model_Llama_33_70B = GroqModel('llama-3.3-70b-versatile',api_key=api_key_groq)
model_OpenAI_35_turbo = OpenAIModel('gpt-3.5-turbo-1106', api_key=api_key_openAI)





#defining the first agent (Search flight agent)
flight_search_agent = Agent[None, Union[FlightDetails, Failed]](
    model=model_Llama_33_70B,
     result_type=Union[FlightDetails, Failed],
       system_prompt=(
        'Use the "flight_search" tool to find a flight'
        'from the given origin to the given destination.'
    ),
    )

@flight_search_agent.tool
async def flight_search(ctx: RunContext[None], origing:str, destination:str) -> Union[FlightDetails, Failed]:
    return FlightDetails(flight_number='AK456') # This line creates an instance of FlightDetails with the attribute flight_number set to 'AK456' and then returns that instance.


async def find_flight(usage: Usage) -> str:
    message_history: Union[list[ModelMessage], None] = None
    for _ in range(3):
        prompt = Prompt.ask('where would you like to fly from and to?')
        result = await flight_search_agent.run(
            prompt,
            message_history=message_history,
            # usage_limits=UsageLimits(request_limit=5, total_tokens_limit=300),
        )
        if isinstance(result.data, FlightDetails):
            return result.data
        else:
             message_history = result.all_messages(
                result_tool_return_content='Please try again.'
            )


# This agent is responsible for extracting the user's seat selection
seat_preference_agent = Agent[None, Union[SeatPreference,None]](
      model=model_Llama_33_70B,
     result_type=Union[SeatPreference, Failed],
       system_prompt=(
      "Extract the user's seat preference."
        'Seats A and F are window seats.'
        'Row 1 is the front row and has extra leg room. '
        'Rows 14, and 20 also have extra leg room. '
    ),
)



async def find_seat(usage: Usage) -> SeatPreference:
    message_history: Union[list[ModelMessage], None] = None
    print("find_seat::ModelMessage", ModelMessage)
    print("find_seat::message_history", message_history)
    while True:
        answer = Prompt.ask('What seat would you like?')

        result = await seat_preference_agent.run(
            answer,
            message_history=message_history,
        )
        if isinstance(result.data, SeatPreference):
            return result.data
        else:
            print('Could not understand seat preference. Please try again.')
            message_history = result.all_messages()
    



async def main():
    usage: Usage = Usage()
    print("Programmatic agent hand-off")
    opt_flight_details = await find_flight(usage)
    print(" opt_flight_details", opt_flight_details)
    if opt_flight_details is not None:
        seat_preference = await find_seat(usage)
        print("seat_preference", seat_preference)
        



asyncio.run(main())
