from agents import Agent, RunContextWrapper, Runner, trace
from pydantic import BaseModel
import asyncio
import rich
from dotenv import load_dotenv

load_dotenv()

class BankContext(BaseModel):
    name: str
    role: str  # "Customer", "BranchOfficer", "ComplianceOfficer", "DigitalAnalyst"
    segment: str | None = None  # "Retail", "SME", "Corporate"
    channel: str | None = None  # "MobileApp", "Branch", "ContactCenter", "Web"
    language: str = "en"        # "en" or "ur"
    risk_level: str | None = None  # "Low", "Medium", "High"

async def dynamic_instructions(ctx: RunContextWrapper[BankContext], agent: Agent):
    c = ctx.context
    base = [
        "Always maintain a helpful, respectful, and compliant tone.",
        "Never ask for OTPs, CVV, full card or account numbers. Never share sensitive data.",
        "Prefer step-by-step, concise guidance. If risk is High, include fraud-warning and escalation.",
        "If user asks for irreversible actions, recommend official channels or in-app secure flows.",
        "If channel is MobileApp or Web, map guidance to on-screen navigation.",
        "If language is 'ur', keep English but include brief Urdu cues in parentheses for clarity.",
        "Tailor jargon and depth to the user's role."
    ]

    role_rules = ""
    if c.role == "Customer":
        role_rules = (
            "Use simple banking language. Emphasize safety, digital self-service steps, and quick resolution. "
            "If SME segment, include business-banking notes. "
            "If High risk_level, add a fraud caution and suggest contacting NBP helpline or visiting branch."
        )
    elif c.role == "BranchOfficer":
        role_rules = (
            "Be concise and operational. Reference NBP processes: KYC/AML checks, risk flags, escalation paths, "
            "ticket creation, and customer education. Provide checklists."
        )
    elif c.role == "ComplianceOfficer":
        role_rules = (
            "Use precise compliance language. Reference KYC/AML/CTR/STR concepts at a high level, "
            "stress documentation and auditability. Do not reveal customer PII in output."
        )
    elif c.role == "DigitalAnalyst":
        role_rules = (
            "Focus on funnels, drop-offs, event tracking, and experiment design. "
            "Propose instrumentation, dashboards, and hypotheses. Avoid customer PII."
        )
    else:
        role_rules = "Default to clear, safe, and compliant assistance."

    risk_rule = ""
    if c.risk_level == "High":
        risk_rule = (
            "User is high risk. Begin with a short fraud warning, avoid transactional specifics, "
            "and advise secure verification via official NBP channels (Helpline 24/7 or nearest branch)."
        )

    channel_rule = ""
    if c.channel in {"MobileApp", "Web"}:
        channel_rule = "Map steps to screen paths (e.g., Home → Cards → Manage Card → Report issue)."

    lang_hint = ""
    if c.language == "ur":
        lang_hint = "After each key step, add a brief roman Urdu cue in parentheses."

    return "\n".join([
        *base,
        f"Role policy: {role_rules}",
        f"Risk policy: {risk_rule or 'No special risk handling required.'}",
        f"Channel policy: {channel_rule or 'Generic channel guidance acceptable.'}",
        f"Language policy: {lang_hint or 'English only is fine.'}",
    ])

bank_agent = Agent(
    name="NBP Agentic Assistant",
    instructions=dynamic_instructions,
)

async def run_demo(prompt: str, context: BankContext, title: str):
    with trace(title):
        result = await Runner.run(
            bank_agent,
            prompt,
            context=context
        )
        rich.print(f"[bold cyan]{title}[/bold cyan]")
        rich.print(f"[bold]Context:[/bold] {context.dict()}")
        rich.print(f"[bold]User Prompt:[/bold] {prompt}")
        rich.print(f"[bold green]Agent Response:[/bold green] {result.final_output}\n")

async def main():
    scenarios = [
        (
            "My debit card is blocked after a suspicious SMS. How can I secure my account using the mobile app?",
            BankContext(
                name="Hamza",
                role="Customer",
                segment="Retail",
                channel="MobileApp",
                language="en",
                risk_level="High"
            ),
            "Scenario 1: Retail Customer (High Risk, Mobile App)"
        ),
        (
            "Customer wants to open an SME current account. What documents should I verify and how do I log the KYC?",
            BankContext(
                name="Ayesha",
                role="BranchOfficer",
                segment="SME",
                channel="Branch",
                language="en",
                risk_level="Medium"
            ),
            "Scenario 2: Branch Officer (SME Onboarding)"
        ),
        (
            "A pattern of rapid transfers triggered AML thresholds. Outline steps for an STR assessment.",
            BankContext(
                name="ComplianceBot",
                role="ComplianceOfficer",
                segment="Retail",
                channel="Web",
                language="en",
                risk_level="High"
            ),
            "Scenario 3: Compliance (AML/STR Review)"
        ),
        (
            "Login drop-off is high between OTP and dashboard. Suggest diagnostics and a quick experiment plan.",
            BankContext(
                name="Bilal",
                role="DigitalAnalyst",
                segment="Retail",
                channel="Web",
                language="en",
                risk_level="Low"
            ),
            "Scenario 4: Digital Analyst (Conversion & Experiment)"
        ),
    ]

    for prompt, context, title in scenarios:
        await run_demo(prompt, context, title)

if __name__ == "__main__":
    asyncio.run(main())
