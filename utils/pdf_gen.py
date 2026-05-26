from fpdf import FPDF
from config import ENTERPRISE_NAME

class ProjectPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.cell(0, 10, ENTERPRISE_NAME, 0, 1, 'C')
        self.set_font('Helvetica', 'I', 10)
        self.cell(0, 10, "Loyiha Hujjati va Shartnoma Tafsilotlari", 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Sahifa {self.page_no()}', 0, 0, 'C')

def generate_user_pdf(user, file_path):
    pdf = ProjectPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)

    # Client Info Section
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, "MIJOZ MA'LUMOTLARI", 0, 1, 'L', True)
    pdf.set_font("Helvetica", size=11)
    
    data = [
        ("Invoist ID:", str(user['tg_id'])),
        ("Mulk egasi:", user['full_name']),
        ("Telefon:", user['phone']),
        ("Manzil:", user['address']),
        ("Ro'yxatdan o'tgan vaqt:", user['created_at'])
    ]
    
    for label, val in data:
        pdf.cell(50, 8, label, 0, 0)
        pdf.cell(0, 8, val, 0, 1)
    
    pdf.ln(10)

    # Project Info Section
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, "LOYIHA PARAMETRLARI", 0, 1, 'L', True)
    pdf.set_font("Helvetica", size=11)
    
    proj_data = [
        ("Loyiha toifasi:", user['loyiha_toifasi']),
        ("Xizmat turi:", user['service_type']),
        ("Bosqich:", user['stage']),
        ("Loyiha turi:", user['tur']),
        ("Ish xolati:", user['status'])
    ]
    
    for label, val in proj_data:
        pdf.cell(50, 8, label, 0, 0)
        pdf.cell(0, 8, val, 0, 1)
        
    pdf.ln(10)

    # Financial Section
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, "MOLIYAVIY HISOBOT", 0, 1, 'L', True)
    pdf.set_font("Helvetica", size=11)
    
    total = user['total_sum'] or 0
    paid = user['paid_sum'] or 0
    balance = total - paid
    
    fin_data = [
        ("Umumiy summa:", f"{total:,.0f} so'm"),
        ("To'langan summa:", f"{paid:,.0f} so'm"),
        ("Qoldiq qarz:", f"{balance:,.0f} so'm")
    ]
    
    for label, val in fin_data:
        pdf.cell(50, 8, label, 0, 0)
        pdf.cell(0, 8, val, 0, 1)

    pdf.ln(20)
    pdf.cell(0, 10, "_" * 30, 0, 1, 'R')
    pdf.cell(0, 5, "Mas'ul shaxs imzosi", 0, 1, 'R')

    pdf.output(file_path)

def generate_full_report_pdf(users, file_path):
    pdf = ProjectPDF('L') # Landscape for tabular data
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(0, 10, "Barcha Loyihalar Hisoboti (PDF)", 0, 1, 'C')
    pdf.ln(5)
    
    # Table Header
    pdf.set_font("Helvetica", 'B', 10)
    pdf.set_fill_color(220, 220, 220)
    col_widths = [10, 40, 60, 30, 30, 30, 30, 15] # No, Name, Category, Total, Paid, Debt, Status, Date
    headers = ["No", "Mulk egasi", "Toifa", "Umumiy", "To'langan", "Qarz", "Holat", "Vaqt"]
    
    for i, h in enumerate(headers):
        pdf.cell(col_widths[i], 10, h, 1, 0, 'C', True)
    pdf.ln()

    # Table Data
    pdf.set_font("Helvetica", size=9)
    for i, user in enumerate(users, start=1):
        total = user['total_sum'] or 0
        paid = user['paid_sum'] or 0
        balance = total - paid
        
        pdf.cell(col_widths[0], 8, str(i), 1, 0, 'C')
        pdf.cell(col_widths[1], 8, str(user['full_name'])[:20], 1, 0, 'L')
        pdf.cell(col_widths[2], 8, str(user['loyiha_toifasi'])[:30], 1, 0, 'L')
        pdf.cell(col_widths[3], 8, f"{total:,.0f}", 1, 0, 'R')
        pdf.cell(col_widths[4], 8, f"{paid:,.0f}", 1, 0, 'R')
        pdf.cell(col_widths[5], 8, f"{balance:,.0f}", 1, 0, 'R')
        pdf.cell(col_widths[6], 8, str(user['status']), 1, 0, 'C')
        pdf.cell(col_widths[7], 8, str(user['created_at'])[:10], 1, 1, 'C')

    pdf.output(file_path)
