from agents import Agent, RunContextWrapper, Runner,trace
from pydantic import BaseModel
#from connection import config
import asyncio
import rich
from dotenv import load_dotenv
load_dotenv()

class TravelPlanning(BaseModel):
    trip_type: str
    traveler_profile: str

travel_planning = TravelPlanning(
    trip_type="Adventure",
    traveler_profile="Solo"
)

async def my_dynamic_instructions(ctx: RunContextWrapper[TravelPlanning], agent: Agent):
    if ctx.context.trip_type == "Adventure" and ctx.context.traveler_profile == "Solo":
        return "Suggest exciting activities, focus on safety tips, recommend social hostels and group tours for meeting people"
    elif ctx.context.trip_type == "Culture" and ctx.context.traveler_profile == "Family":
        return "Focus on educational attractions, kid-friendly museums, interactive experiences, family accommodations"
    elif ctx.context.trip_type == "Business" and ctx.context.traveler_profile == "Executive":
        return "Emphasize efficiency, airport proximity, business centers, reliable wifi, premium lounges."

travel_planning_agent = Agent(
    name="Travel Planning Agent",
    instructions=my_dynamic_instructions,
    
)

async def main():
   with trace("Travel Planning"):
        result = await Runner.run(
            travel_planning_agent,
            "Suggest Travel Plan",
            
            context=travel_planning
        )
        rich.print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
