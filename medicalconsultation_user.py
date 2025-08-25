from agents import Agent, RunContextWrapper, Runner, trace
from pydantic import BaseModel
from connection import config
import asyncio
import rich

class MedicalConsultation(BaseModel):
    name: str
    user_type: str

medicalconsultant_user = MedicalConsultation(
    name="Syeda",
    user_type="Patient"
)

async def my_dynamic_instructions(ctx: RunContextWrapper[MedicalConsultation], agent: Agent):
    if ctx.context.user_type == "Patient":
        return """Use simple, non-technical language. Explain medical terms in everyday words. Be empathetic and reassuring."""
    elif ctx.context.user_type == "Medical Student":
        return """Use moderate medical terminology with explanations. Include learning opportunities."""
    elif ctx.context.user_type == "Doctor":
        return """Use full medical terminology, abbreviations, and clinical language. Be concise and professional."""

medicalconsultation_agent = Agent(
    name="Medical Consultation Agent",
    instructions=my_dynamic_instructions,
    
)

async def main():
    with trace("Medical Consultation User"):
        result = await Runner.run(
            medicalconsultation_agent,
            "Describe Blood Pressure Disease?",
            run_config=config,
            context=medicalconsultant_user
        )
        rich.print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
