from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import datetime
from pathlib import Path
from typing import Dict

REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# PUBLIC_INTERFACE
def generate_pdf_report(session_name: str, user_name: str, city: str, income: float, expenses: float, analysis: Dict, author: str = "FinMate") -> str:
    """Generate a PDF report for the provided session data and return the file path."""
    path = REPORTS_DIR / f"{session_name}.pdf"
    c = canvas.Canvas(str(path), pagesize=LETTER)
    width, height = LETTER

    c.setTitle(f"FinMate Report - {session_name}")
    c.setAuthor(author)

    y = height - inch
    c.setFont("Helvetica-Bold", 16)
    c.drawString(inch, y, "FinMate — Personal Finance Report")
    y -= 0.3 * inch
    c.setFont("Helvetica", 10)
    c.drawString(inch, y, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    y -= 0.2 * inch

    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, y, "User Details")
    y -= 0.2 * inch
    c.setFont("Helvetica", 10)
    c.drawString(inch, y, f"Name: {user_name}")
    y -= 0.18 * inch
    c.drawString(inch, y, f"City: {city}")
    y -= 0.18 * inch
    c.drawString(inch, y, f"Income: ${income:,.2f}")
    y -= 0.18 * inch
    c.drawString(inch, y, f"Expenses: ${expenses:,.2f}")
    y -= 0.25 * inch

    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, y, "Key Metrics")
    y -= 0.2 * inch
    c.setFont("Helvetica", 10)
    c.drawString(inch, y, f"Savings Rate: {analysis['savings_rate_pct']}%")
    y -= 0.18 * inch
    c.drawString(inch, y, f"Monthly Savings: ${analysis['monthly_savings']:,.2f}")
    y -= 0.18 * inch
    c.drawString(inch, y, f"Emergency Fund Target: ${analysis['emergency_fund_target']:,.2f}")
    y -= 0.18 * inch
    c.drawString(inch, y, f"Investment Budget: ${analysis['investment_budget']:,.2f}")
    y -= 0.25 * inch

    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, y, "Allocations")
    y -= 0.2 * inch
    c.setFont("Helvetica", 10)
    for k, v in analysis["allocations"].items():
        c.drawString(inch, y, f"{k}: ${v:,.2f}")
        y -= 0.18 * inch
        if y < inch:
            c.showPage()
            y = height - inch
            c.setFont("Helvetica", 10)

    y -= 0.1 * inch
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, y, "Recommendations")
    y -= 0.2 * inch
    c.setFont("Helvetica", 10)
    for rec in analysis["recommendations"]:
        for line in wrap_text(rec, max_chars=90):
            c.drawString(inch, y, f"- {line}")
            y -= 0.18 * inch
            if y < inch:
                c.showPage()
                y = height - inch
                c.setFont("Helvetica", 10)

    c.showPage()
    c.save()
    return str(path)

def wrap_text(text: str, max_chars: int = 90):
    """Yield wrapped lines for given text with a basic character limit."""
    words = text.split()
    line = []
    count = 0
    for w in words:
        add = len(w) + (1 if line else 0)
        if count + add > max_chars:
            yield " ".join(line)
            line = [w]
            count = len(w)
        else:
            line.append(w)
            count += add
    if line:
        yield " ".join(line)
