from agents import Agent, RunContextWrapper, Runner, trace
from pydantic import BaseModel, Field
from typing import Literal, Optional
import asyncio
import rich
from dotenv import load_dotenv

load_dotenv()

# ------------------ Context Model for a Bank ------------------ #
class BankContext(BaseModel):
    audience_department: Literal["Digital Banking", "Fraud Risk", "Compliance", "IT/Engineering", "Customer Support"]
    audience_level: Literal["Executive", "Manager", "Analyst", "Engineer", "Associate"] = "Manager"
    objective: Literal[
        "Customer Communication",
        "Process Design",
        "Risk Review",
        "Feature Ideation",
        "Analytics Summary"
    ] = "Customer Communication"
    risk_focus: Literal["Low", "Medium", "High"] = "Low"
    language: Literal["English", "Urdu"] = "English"
    channel: Literal["Mobile", "Branch", "Core Banking", "Internet Banking"] = "Mobile"
    region: Optional[str] = Field(default="Pakistan", description="Geo context helpful for tone/regulations")

# Example: default context for National Bank of Pakistan – Digital Dept.
nbp_digital_ctx = BankContext(
    audience_department="Digital Banking",
    audience_level="Manager",
    objective="Customer Communication",
    risk_focus="Medium",
    language="English",
    channel="Mobile",
    region="Pakistan"
)

# ------------------ Dynamic Instructions ------------------ #
async def banking_dynamic_instructions(ctx: RunContextWrapper[BankContext], agent: Agent):
    c = ctx.context

    # Base bank tone
    base_tone = [
        "Be concise, professional, and customer-centric.",
        "Prefer bullet points and numbered steps.",
        "When giving recommendations, separate 'Now', 'Next', and 'Later'.",
        "Always consider Pakistani banking context (NBP) and local regulations at a high level.",
    ]

    # Department-specific guidance
    if c.audience_department == "Digital Banking":
        dept = [
            "Focus on mobile app UX, onboarding flows, uptime, and feature adoption.",
            "Avoid deep technical stack talk; highlight impact, KPIs, and customer journey.",
        ]
    elif c.audience_department == "Fraud Risk":
        dept = [
            "Emphasize risk signals, thresholds, false positive trade-offs, and explainability.",
            "Include actions for monitoring, alerts, case management, and audit trails.",
        ]
    elif c.audience_department == "Compliance":
        dept = [
            "Use formal tone; reference policy/process alignment, approvals, and documentation.",
            "Avoid legal advice; recommend consultation with compliance/legal for specifics.",
        ]
    elif c.audience_department == "IT/Engineering":
        dept = [
            "Be technical; include APIs, data flows, SLAs, error handling, and observability.",
            "Call out security controls, IAM, encryption, and dependency risks.",
        ]
    else:  # Customer Support
        dept = [
            "Use simple, empathetic language and short sentences.",
            "Offer step-by-step resolution paths and escalation criteria.",
        ]

    # Objective-specific guidance
    if c.objective == "Customer Communication":
        obj = [
            "Write in clear, polite tone suitable for push notification/email/in-app message.",
            "Avoid jargon; include a call to action.",
        ]
    elif c.objective == "Process Design":
        obj = [
            "Deliver high-level process with inputs/outputs, RACI, and key controls.",
            "Add quick win suggestions and measurable acceptance criteria.",
        ]
    elif c.objective == "Risk Review":
        obj = [
            "Identify top risks, likelihood × impact, detection/response, and residual risk.",
            "Propose monitoring metrics and review cadence.",
        ]
    elif c.objective == "Feature Ideation":
        obj = [
            "List 3–5 features with value hypothesis, success metric, and simple experiment plan.",
        ]
    else:  # Analytics Summary
        obj = [
            "Provide 3 key insights, 3 drivers, and 3 recommended actions.",
            "If you assume data, clearly label as assumption.",
        ]

    # Risk focus modifier
    if c.risk_focus == "High":
        risk = [
            "Be risk-first: prioritize controls, approvals, and rollout gating.",
            "Flag any data privacy or regulatory exposure explicitly.",
        ]
    elif c.risk_focus == "Medium":
        risk = [
            "Balance growth with safeguards; propose phased rollout and monitoring.",
        ]
    else:
        risk = [
            "Favor speed with basic guardrails; plan a fast feedback loop.",
        ]

    # Language
    lang = []
    if c.language == "Urdu":
        lang = [
            "Respond in simple Roman Urdu suitable for a broad audience in Pakistan.",
        ]
    else:
        lang = ["Respond in clear, simple English."]

    # Channel-specific nudges
    if c.channel == "Mobile":
        ch = [
            "Consider small screen UI and push notifications; suggest minimal taps.",
        ]
    elif c.channel == "Internet Banking":
        ch = [
            "Assume desktop web; consider session timeouts and 2FA prompts.",
        ]
    elif c.channel == "Core Banking":
        ch = [
            "Assume back-office operators and strict auditing; minimize manual steps.",
        ]
    else:  # Branch
        ch = [
            "Assume in-person staff workflows and printed confirmations.",
        ]

    # Region
    reg = [f"Region: {c.region}. Consider local customer expectations and banking norms."]

    # Stitch all parts
    all_parts = base_tone + dept + obj + risk + lang + ch + reg

    # Return as a single instruction string
    return "\n".join(all_parts)

# ------------------ Agent ------------------ #
banking_agent = Agent(
    name="NBP Agentic AI Demo",
    instructions=banking_dynamic_instructions,
)

# ------------------ Demo Prompt ------------------ #
demo_prompt = """
We need a short plan and draft message for this scenario:
A legitimate NBP customer’s card transaction was declined on our Mobile channel due to risk rules.
1) Give a brief plan for immediate handling (Now), next steps (Next), and follow-ups (Later).
2) Draft a customer-facing message suitable for in-app notification.
"""

# ------------------ Run 3 Audience Variations ------------------ #
async def run_all():
    with trace("NBP Digital Banking"):
        out1 = await Runner.run(
            banking_agent,
            demo_prompt,
            context=nbp_digital_ctx
        )
        rich.print("\n[bold green]---- Digital Banking (Manager) ----[/bold green]")
        rich.print(out1.final_output)

    fraud_ctx = BankContext(
        audience_department="Fraud Risk",
        audience_level="Analyst",
        objective="Risk Review",
        risk_focus="High",
        language="English",
        channel="Mobile",
        region="Pakistan"
    )
    with trace("NBP Fraud Risk"):
        out2 = await Runner.run(banking_agent, demo_prompt, context=fraud_ctx)
        rich.print("\n[bold yellow]---- Fraud Risk (Analyst) ----[/bold yellow]")
        rich.print(out2.final_output)

    compliance_ctx = BankContext(
        audience_department="Compliance",
        audience_level="Manager",
        objective="Process Design",
        risk_focus="Medium",
        language="English",
        channel="Core Banking",
        region="Pakistan"
    )
    with trace("NBP Compliance"):
        out3 = await Runner.run(banking_agent, demo_prompt, context=compliance_ctx)
        rich.print("\n[bold cyan]---- Compliance (Manager) ----[/bold cyan]")
        rich.print(out3.final_output)

if __name__ == "__main__":
    asyncio.run(run_all())
