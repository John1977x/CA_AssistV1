"""
Seed script to create 15 predefined assignment templates
Run with: python seed_assignment_templates.py
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.assignment import AssignmentTemplate, AssignmentTemplateStep
from app.core.config import settings

# Create async engine
engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

TEMPLATES = [
    {
        "title": "GST Return Filing",
        "description": "Complete GST return filing process with verification and submission",
        "category": "GST",
        "difficulty_level": "MEDIUM",
        "estimated_hours": 4,
        "steps": [
            {
                "step_number": 1,
                "title": "Gather Documents",
                "description": "Collect all invoices and supporting documents",
                "instructions": "Organize all GST invoices, credit notes, and debit notes for the period",
                "estimated_hours": 1,
            },
            {
                "step_number": 2,
                "title": "Verify Transactions",
                "description": "Verify all transactions and reconcile amounts",
                "instructions": "Cross-check invoice amounts with bank statements and ledger",
                "estimated_hours": 1.5,
            },
            {
                "step_number": 3,
                "title": "File Return",
                "description": "File the GST return on the portal",
                "instructions": "Login to GST portal and submit the return",
                "estimated_hours": 1,
            },
            {
                "step_number": 4,
                "title": "Confirmation",
                "description": "Get filing confirmation and archive documents",
                "instructions": "Download and save the filing confirmation",
                "estimated_hours": 0.5,
            },
        ],
    },
    {
        "title": "Income Tax Return (ITR-1)",
        "description": "File individual income tax return for salaried individuals",
        "category": "ITR",
        "difficulty_level": "MEDIUM",
        "estimated_hours": 5,
        "steps": [
            {
                "step_number": 1,
                "title": "Collect Income Documents",
                "description": "Gather salary slips, interest certificates, and other income proofs",
                "instructions": "Collect Form 16, bank statements, and investment proofs",
                "estimated_hours": 1,
            },
            {
                "step_number": 2,
                "title": "Calculate Deductions",
                "description": "Calculate eligible deductions under Section 80C, 80D, etc.",
                "instructions": "Prepare list of investments and insurance premiums",
                "estimated_hours": 1.5,
            },
            {
                "step_number": 3,
                "title": "Prepare ITR Form",
                "description": "Fill ITR-1 form with all details",
                "instructions": "Use income tax software or manual form",
                "estimated_hours": 1.5,
            },
            {
                "step_number": 4,
                "title": "Verify and File",
                "description": "Verify details and file the return",
                "instructions": "Review all entries and submit electronically",
                "estimated_hours": 1,
            },
        ],
    },
    {
        "title": "TDS Compliance",
        "description": "Handle Tax Deducted at Source (TDS) compliance and filing",
        "category": "TDS",
        "difficulty_level": "HARD",
        "estimated_hours": 6,
        "steps": [
            {
                "step_number": 1,
                "title": "Identify TDS Transactions",
                "description": "Identify all transactions subject to TDS",
                "instructions": "Review payments to contractors, consultants, and vendors",
                "estimated_hours": 1,
            },
            {
                "step_number": 2,
                "title": "Calculate TDS Amount",
                "description": "Calculate TDS at applicable rates",
                "instructions": "Apply correct TDS rates based on transaction type",
                "estimated_hours": 1.5,
            },
            {
                "step_number": 3,
                "title": "Deposit TDS",
                "description": "Deposit TDS to government account",
                "instructions": "Deposit through NEFT/RTGS before due date",
                "estimated_hours": 1,
            },
            {
                "step_number": 4,
                "title": "File TDS Return",
                "description": "File quarterly TDS return",
                "instructions": "File Form 24Q on portal",
                "estimated_hours": 1.5,
            },
            {
                "step_number": 5,
                "title": "Issue Certificates",
                "description": "Issue TDS certificates to deductees",
                "instructions": "Generate and send Form 16A",
                "estimated_hours": 1,
            },
        ],
    },
    {
        "title": "Audit Preparation",
        "description": "Prepare documents and records for statutory audit",
        "category": "AUDIT",
        "difficulty_level": "HARD",
        "estimated_hours": 8,
        "steps": [
            {
                "step_number": 1,
                "title": "Organize Financial Records",
                "description": "Organize all financial statements and ledgers",
                "instructions": "Prepare trial balance and general ledger",
                "estimated_hours": 2,
            },
            {
                "step_number": 2,
                "title": "Prepare Schedules",
                "description": "Prepare detailed schedules for audit",
                "instructions": "Create schedules for assets, liabilities, and equity",
                "estimated_hours": 2,
            },
            {
                "step_number": 3,
                "title": "Reconcile Accounts",
                "description": "Reconcile bank accounts and other accounts",
                "instructions": "Prepare bank reconciliation statements",
                "estimated_hours": 1.5,
            },
            {
                "step_number": 4,
                "title": "Prepare Audit File",
                "description": "Compile all documents in audit file",
                "instructions": "Organize documents in chronological order",
                "estimated_hours": 1.5,
            },
            {
                "step_number": 5,
                "title": "Coordinate with Auditor",
                "description": "Coordinate with auditor and provide clarifications",
                "instructions": "Respond to auditor queries promptly",
                "estimated_hours": 1,
            },
        ],
    },
    {
        "title": "Payroll Processing",
        "description": "Process monthly payroll and generate salary slips",
        "category": "PAYROLL",
        "difficulty_level": "MEDIUM",
        "estimated_hours": 4,
        "steps": [
            {
                "step_number": 1,
                "title": "Collect Attendance Data",
                "description": "Collect attendance and leave data",
                "instructions": "Get attendance records from HR system",
                "estimated_hours": 0.5,
            },
            {
                "step_number": 2,
                "title": "Calculate Salary",
                "description": "Calculate gross salary and deductions",
                "instructions": "Apply salary structure and calculate net pay",
                "estimated_hours": 1.5,
            },
            {
                "step_number": 3,
                "title": "Generate Salary Slips",
                "description": "Generate and distribute salary slips",
                "instructions": "Create salary slips for all employees",
                "estimated_hours": 1,
            },
            {
                "step_number": 4,
                "title": "Process Payment",
                "description": "Process salary payment to employees",
                "instructions": "Transfer salary through bank",
                "estimated_hours": 1,
            },
        ],
    },
    {
        "title": "Bank Reconciliation",
        "description": "Reconcile bank statements with accounting records",
        "category": "ACCOUNTING",
        "difficulty_level": "EASY",
        "estimated_hours": 2,
        "steps": [
            {
                "step_number": 1,
                "title": "Collect Bank Statement",
                "description": "Obtain bank statement from bank",
                "instructions": "Download statement from online banking",
                "estimated_hours": 0.25,
            },
            {
                "step_number": 2,
                "title": "Compare Transactions",
                "description": "Compare bank transactions with ledger",
                "instructions": "Match each transaction in bank statement",
                "estimated_hours": 1,
            },
            {
                "step_number": 3,
                "title": "Identify Differences",
                "description": "Identify and investigate differences",
                "instructions": "Note outstanding checks and deposits",
                "estimated_hours": 0.5,
            },
            {
                "step_number": 4,
                "title": "Prepare Reconciliation",
                "description": "Prepare bank reconciliation statement",
                "instructions": "Document all reconciling items",
                "estimated_hours": 0.25,
            },
        ],
    },
    {
        "title": "Invoice Processing",
        "description": "Process and verify vendor invoices",
        "category": "ACCOUNTING",
        "difficulty_level": "EASY",
        "estimated_hours": 3,
        "steps": [
            {
                "step_number": 1,
                "title": "Receive Invoice",
                "description": "Receive and verify invoice details",
                "instructions": "Check invoice number, date, and amount",
                "estimated_hours": 0.5,
            },
            {
                "step_number": 2,
                "title": "Verify with PO",
                "description": "Verify invoice against purchase order",
                "instructions": "Match quantity, rate, and terms",
                "estimated_hours": 1,
            },
            {
                "step_number": 3,
                "title": "Check Calculations",
                "description": "Verify mathematical calculations",
                "instructions": "Check GST, discounts, and total amount",
                "estimated_hours": 0.75,
            },
            {
                "step_number": 4,
                "title": "Record in System",
                "description": "Record invoice in accounting system",
                "instructions": "Enter invoice details in software",
                "estimated_hours": 0.75,
            },
        ],
    },
    {
        "title": "Expense Report Review",
        "description": "Review and approve employee expense reports",
        "category": "ACCOUNTING",
        "difficulty_level": "EASY",
        "estimated_hours": 2,
        "steps": [
            {
                "step_number": 1,
                "title": "Collect Expense Reports",
                "description": "Collect all submitted expense reports",
                "instructions": "Get reports from employees",
                "estimated_hours": 0.25,
            },
            {
                "step_number": 2,
                "title": "Verify Receipts",
                "description": "Verify receipts and supporting documents",
                "instructions": "Check all receipts are attached",
                "estimated_hours": 1,
            },
            {
                "step_number": 3,
                "title": "Approve Expenses",
                "description": "Approve eligible expenses",
                "instructions": "Verify against policy and approve",
                "estimated_hours": 0.5,
            },
            {
                "step_number": 4,
                "title": "Process Reimbursement",
                "description": "Process reimbursement to employees",
                "instructions": "Transfer approved amounts",
                "estimated_hours": 0.25,
            },
        ],
    },
    {
        "title": "Financial Statement Preparation",
        "description": "Prepare monthly/quarterly financial statements",
        "category": "ACCOUNTING",
        "difficulty_level": "HARD",
        "estimated_hours": 6,
        "steps": [
            {
                "step_number": 1,
                "title": "Close Accounts",
                "description": "Close temporary accounts",
                "instructions": "Post closing entries",
                "estimated_hours": 1,
            },
            {
                "step_number": 2,
                "title": "Prepare Trial Balance",
                "description": "Prepare adjusted trial balance",
                "instructions": "Include all adjusting entries",
                "estimated_hours": 1,
            },
            {
                "step_number": 3,
                "title": "Create Income Statement",
                "description": "Prepare income statement",
                "instructions": "Calculate revenue, expenses, and profit",
                "estimated_hours": 1.5,
            },
            {
                "step_number": 4,
                "title": "Create Balance Sheet",
                "description": "Prepare balance sheet",
                "instructions": "List assets, liabilities, and equity",
                "estimated_hours": 1.5,
            },
            {
                "step_number": 5,
                "title": "Review and Finalize",
                "description": "Review statements and finalize",
                "instructions": "Verify all figures and approve",
                "estimated_hours": 1,
            },
        ],
    },
    {
        "title": "Compliance Documentation",
        "description": "Prepare and maintain compliance documentation",
        "category": "COMPLIANCE",
        "difficulty_level": "MEDIUM",
        "estimated_hours": 4,
        "steps": [
            {
                "step_number": 1,
                "title": "Identify Requirements",
                "description": "Identify compliance requirements",
                "instructions": "Review applicable laws and regulations",
                "estimated_hours": 1,
            },
            {
                "step_number": 2,
                "title": "Prepare Documents",
                "description": "Prepare required documents",
                "instructions": "Create compliance checklists and forms",
                "estimated_hours": 1.5,
            },
            {
                "step_number": 3,
                "title": "Maintain Records",
                "description": "Maintain compliance records",
                "instructions": "Organize and file all documents",
                "estimated_hours": 1,
            },
            {
                "step_number": 4,
                "title": "Review Compliance",
                "description": "Review compliance status",
                "instructions": "Verify all requirements are met",
                "estimated_hours": 0.5,
            },
        ],
    },
    {
        "title": "Tax Planning",
        "description": "Develop tax planning strategies for clients",
        "category": "TAX",
        "difficulty_level": "HARD",
        "estimated_hours": 5,
        "steps": [
            {
                "step_number": 1,
                "title": "Analyze Financial Position",
                "description": "Analyze client's financial position",
                "instructions": "Review income, expenses, and investments",
                "estimated_hours": 1.5,
            },
            {
                "step_number": 2,
                "title": "Identify Tax Opportunities",
                "description": "Identify tax saving opportunities",
                "instructions": "Review deductions and exemptions",
                "estimated_hours": 1.5,
            },
            {
                "step_number": 3,
                "title": "Prepare Tax Plan",
                "description": "Prepare comprehensive tax plan",
                "instructions": "Document strategies and recommendations",
                "estimated_hours": 1.5,
            },
            {
                "step_number": 4,
                "title": "Present to Client",
                "description": "Present plan to client",
                "instructions": "Explain benefits and implementation",
                "estimated_hours": 0.5,
            },
        ],
    },
    {
        "title": "Client Onboarding",
        "description": "Complete client onboarding process",
        "category": "CLIENT",
        "difficulty_level": "MEDIUM",
        "estimated_hours": 3,
        "steps": [
            {
                "step_number": 1,
                "title": "Collect Information",
                "description": "Collect client information and documents",
                "instructions": "Get PAN, Aadhaar, and business details",
                "estimated_hours": 1,
            },
            {
                "step_number": 2,
                "title": "Verify Documents",
                "description": "Verify all submitted documents",
                "instructions": "Check authenticity and completeness",
                "estimated_hours": 0.75,
            },
            {
                "step_number": 3,
                "title": "Setup Systems",
                "description": "Setup client in accounting systems",
                "instructions": "Create client profile and accounts",
                "estimated_hours": 0.75,
            },
            {
                "step_number": 4,
                "title": "Provide Orientation",
                "description": "Provide client orientation",
                "instructions": "Explain processes and expectations",
                "estimated_hours": 0.5,
            },
        ],
    },
    {
        "title": "Data Entry and Verification",
        "description": "Enter and verify financial data",
        "category": "DATA",
        "difficulty_level": "EASY",
        "estimated_hours": 4,
        "steps": [
            {
                "step_number": 1,
                "title": "Collect Source Documents",
                "description": "Collect all source documents",
                "instructions": "Get invoices, receipts, and statements",
                "estimated_hours": 0.5,
            },
            {
                "step_number": 2,
                "title": "Enter Data",
                "description": "Enter data into system",
                "instructions": "Input all transactions accurately",
                "estimated_hours": 2,
            },
            {
                "step_number": 3,
                "title": "Verify Entries",
                "description": "Verify entered data",
                "instructions": "Cross-check with source documents",
                "estimated_hours": 1,
            },
            {
                "step_number": 4,
                "title": "Generate Report",
                "description": "Generate verification report",
                "instructions": "Document any discrepancies",
                "estimated_hours": 0.5,
            },
        ],
    },
    {
        "title": "Quarterly Review",
        "description": "Conduct quarterly business and financial review",
        "category": "REVIEW",
        "difficulty_level": "MEDIUM",
        "estimated_hours": 4,
        "steps": [
            {
                "step_number": 1,
                "title": "Prepare Financial Summary",
                "description": "Prepare quarterly financial summary",
                "instructions": "Compile P&L and balance sheet",
                "estimated_hours": 1,
            },
            {
                "step_number": 2,
                "title": "Analyze Performance",
                "description": "Analyze business performance",
                "instructions": "Compare with previous quarters",
                "estimated_hours": 1,
            },
            {
                "step_number": 3,
                "title": "Identify Issues",
                "description": "Identify any issues or concerns",
                "instructions": "Note variances and anomalies",
                "estimated_hours": 1,
            },
            {
                "step_number": 4,
                "title": "Prepare Report",
                "description": "Prepare quarterly review report",
                "instructions": "Document findings and recommendations",
                "estimated_hours": 1,
            },
        ],
    },
]


async def seed_templates():
    """Seed assignment templates into database"""
    async with engine.begin() as conn:
        # Create tables if they don't exist
        from app.db.session import Base
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        try:
            for template_data in TEMPLATES:
                steps_data = template_data.pop("steps", [])
                
                # Create template
                template = AssignmentTemplate(
                    tenant_id=1,  # Default tenant
                    title=template_data["title"],
                    description=template_data["description"],
                    category=template_data["category"],
                    difficulty_level=template_data["difficulty_level"],
                    estimated_hours=template_data["estimated_hours"],
                    total_steps=len(steps_data),
                    is_active=True,
                )
                session.add(template)
                await session.flush()

                # Create steps
                for step_data in steps_data:
                    step = AssignmentTemplateStep(
                        template_id=template.template_id,
                        **step_data,
                        is_required=True,
                    )
                    session.add(step)

            await session.commit()
            print(f"✅ Successfully seeded {len(TEMPLATES)} assignment templates!")
            print("Templates created:")
            for template_data in TEMPLATES:
                print(f"  - {template_data['title']} ({template_data['category']})")

        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding templates: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed_templates())
