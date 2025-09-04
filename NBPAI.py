import asyncio
from dotenv import load_dotenv
from pydantic import BaseModel
from agents import Agent, RunContextWrapper, Runner
import rich

load_dotenv()

class BankContext(BaseModel):
    name: str
    role: str
    segment: str | None = None
    channel: str | None = None
    language: str = "en"
    risk_level: str | None = None

async def dynamic_instructions(ctx: RunContextWrapper[BankContext], agent: Agent):
    c = ctx.context
    return f"You are assisting role={c.role}, channel={c.channel}, lang={c.language}, risk={c.risk_level}"

bank_agent = Agent(
    name="NBP Agentic Assistant",
    instructions=dynamic_instructions,
)

async def main():
    print("👋 Welcome to NBP Agentic Assistant! Please configure your profile:")

    name = input("Enter your name: ")
    role = input("Select role (Customer / BranchOfficer / ComplianceOfficer / DigitalAnalyst): ")
    channel = input("Select channel (Web / MobileApp / Branch / ContactCenter): ")
    language = input("Select language (en / ur): ")
    risk = input("Select risk level (Low / Medium / High): ")

    context = BankContext(
        name=name or "Guest",
        role=role,
        channel=channel,
        language=language,
        risk_level=risk,
        segment="Retail",
    )

    print(f"✅ Thank you {name}! You can now ask your banking queries.")
    print("Type 'exit' to quit.\n")

    while True:
        user_message = input("You: ")
        if user_message.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        result = await Runner.run(
            bank_agent,
            user_message,
            context=context
        )
        rich.print("Assistant:", result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
