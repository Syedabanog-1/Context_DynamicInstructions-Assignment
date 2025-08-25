from agents import Agent, RunContextWrapper, Runner, trace
from pydantic import BaseModel
from connection import config 
import asyncio
import rich

class Person(BaseModel):
    name: str
    user_level: str

person = Person(
    name="Ali",
    user_level="junior"
)

async def my_dynamic_instructions(ctx: RunContextWrapper[Person], agent: Agent):
    if ctx.context.user_level in ["junior", "mid_level"]:
        return "Keep your answers simple and easy to understand."
    elif ctx.context.user_level == "phd":
        return "Keep your vocabulary advanced, as if you are talking to a PhD-level person."
    else:
        return "Provide clear and balanced explanations."

personal_agent = Agent(
    name="Agent",
    instructions=my_dynamic_instructions,
    
)

async def main():
   with trace("Learn Dynamic Instructions"):
        result = await Runner.run(
            personal_agent,
            "What is light?",
            run_config=config,
            context=person
        )
        rich.print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
