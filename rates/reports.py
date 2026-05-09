import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse
from rates.models import GoldSilverRate

def generate_rate_pdf(metal):
    """
    Generate a PDF report for the given metal's recent price history.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    styles = getSampleStyleSheet()
    title = f"{metal.capitalize()} Price History Report"
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 12))
    
    # Table Header
    data = [['Timestamp', 'Price (USD/oz)', 'Change (%)']]
    
    # Recent history
    history = GoldSilverRate.objects.filter(metal=metal).order_by('-timestamp')[:50]
    for h in history:
        data.append([
            h.timestamp.strftime("%Y-%m-%d %H:%M"),
            f"${h.price_usd:.2f}",
            f"{h.percentage_change:+.3f}%"
        ])
    
    # Create Table
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(t)
    doc.build(elements)
    
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
