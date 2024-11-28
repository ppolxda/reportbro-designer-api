from fpdf import FPDF

pdf = FPDF()
pdf.add_font("DejaVuSans", fname="reportbro_designer_api/static/fonts/DejaVuSans.ttf", uni=True)
pdf.set_font("DejaVuSans")
pdf.add_page()
pdf.text(50, 50, "☑☐")
pdf.output("emoji.pdf")
