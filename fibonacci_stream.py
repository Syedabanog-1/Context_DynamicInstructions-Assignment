from agents import Agent, RunContextWrapper, Runner, trace
from pydantic import BaseModel
import asyncio
import rich
from dotenv import load_dotenv
load_dotenv()

class Fibonacci(BaseModel):
    n: int

fseries = Fibonacci(
    n=10
)

def fibonacci(n: int):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

async def my_dynamic_instructions(ctx: RunContextWrapper[Fibonacci], agent: Agent):
    series = list(fibonacci(ctx.context.n))
    return f"Fibonacci series up to {ctx.context.n} terms: {series}"

fibonacci_agent = Agent(
    name="FibonacciAgent",
    instructions=my_dynamic_instructions,
)

async def main():
    with trace("Learn Dynamic Instructions"):
        result =  Runner.run_streamed(
            fibonacci_agent,
            "Generate Fibonacci series",
            context=fseries
        )
        rich.print(result)

if __name__ == "__main__":
    asyncio.run(main())
