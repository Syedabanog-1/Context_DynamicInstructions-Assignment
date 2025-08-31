from agents import Agent, RunContextWrapper, Runner, trace
from pydantic import BaseModel
#from connection import config
import asyncio
import rich
from dotenv import load_dotenv
load_dotenv()


class AirlineBooking(BaseModel):
    seat_preference: str
    travel_experience: str

airline_booking = AirlineBooking(
    seat_preference="Window",
    travel_experience="First_time"
)

async def my_dynamic_instructions(ctx: RunContextWrapper[AirlineBooking], agent: Agent):
    if ctx.context.seat_preference == "Window" and ctx.context.travel_experience == "First_time":
        return "Explain window benefits, mention scenic views, reassure about flight experience."
    elif ctx.context.seat_preference == "Aisle" and ctx.context.travel_experience == "Occasional":
        return "Provide the best suggestion"
    elif ctx.context.seat_preference == "Middle" and ctx.context.travel_experience == "Frequent":
        return "Acknowledge the compromise, suggest strategies, offer alternatives"
    elif ctx.context.seat_preference == "Any" and ctx.context.travel_experience == "Premium":
        return "Highlight luxury options, upgrades, priority boarding"

airlinebooking_agent = Agent(
    name="Airline Booking Agent",
    instructions=my_dynamic_instructions,
    
)

async def main():
   with trace("Airline Booking"):
        result = await Runner.run(
            airlinebooking_agent,
            "Suggest seat and travel experience tips",
            
            context=airline_booking
        )
        rich.print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
