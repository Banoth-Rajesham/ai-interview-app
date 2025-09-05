from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "AI Interview Report", 0, 1, "C")

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

def generate_pdf(candidate_name, role, summary, questions, answers):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Candidate: {candidate_name}", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Role: {role}", ln=True)
    pdf.cell(0, 10, f"Overall Score: {summary.get('overall_score','N/A')}/10", ln=True)
    pdf.cell(0, 10, f"Recommendation: {summary.get('recommendation','N/A')}", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Detailed Q&A:", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    for i, (q, a) in enumerate(zip(questions, answers), 1):
        pdf.multi_cell(0, 10, f"Q{i}: {q.get('text','')}")
        pdf.multi_cell(0, 10, f"Answer: {a.get('answer','')}")
        pdf.multi_cell(0, 10, f"Feedback: {a.get('feedback','')} (Score: {a.get('score','N/A')}/10)")
        pdf.ln(5)
    return pdf.output(dest="S").encode("latin-1")
