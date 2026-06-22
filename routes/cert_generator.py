"""
Certificate PDF Generator — Peaceful, Happy Blue Theme Layout
"""

import os
import hashlib
import qrcode
from datetime import date

try:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.colors import HexColor, white
    from reportlab.pdfgen import canvas as rl_canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CERTIFICATES_DIR = os.path.join(_BASE, 'certificate_system', 'backend', 'uploads', 'certificates')
QR_CODES_DIR     = os.path.join(_BASE, 'certificate_system', 'backend', 'uploads', 'qr_codes')


def ensure_dirs():
    os.makedirs(CERTIFICATES_DIR, exist_ok=True)
    os.makedirs(QR_CODES_DIR, exist_ok=True)


def _fmt(d) -> str:
    if isinstance(d, date):
        return d.strftime('%B %d, %Y')
    try:
        from datetime import datetime
        return datetime.strptime(str(d), '%Y-%m-%d').strftime('%B %d, %Y')
    except Exception:
        return str(d)


def _tc(s: str) -> str:
    return ' '.join(w.capitalize() for w in str(s).split())


def _fit(c, text, font, size, max_w):
    while size > 7 and c.stringWidth(text, font, size) > max_w:
        size -= 1
    return text, size


def _center(c, text, font, size, color, y, max_w, page_w, charSpace=0):
    text, size = _fit(c, text, font, size, max_w)
    c.setFont(font, size)
    c.setFillColor(color)
    
    if charSpace > 0:
        total_w = sum(c.stringWidth(char, font, size) for char in text) + (len(text) - 1) * charSpace
        x = (page_w - total_w) / 2
        for char in text:
            c.drawString(x, y, char)
            x += c.stringWidth(char, font, size) + charSpace
        return total_w, size
    else:
        tw = c.stringWidth(text, font, size)
        c.drawString((page_w - tw) / 2, y, text)
        return tw, size


# ─────────────────────────────────────────────────────────────────────────────

def generate_qr_code(certificate_id: str, verification_url: str) -> str:
    ensure_dirs()
    qr = qrcode.QRCode(version=1, box_size=5, border=0)
    qr.add_data(verification_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='#1E3A8A', back_color='white') # Dark blue QR code
    fp = os.path.join(QR_CODES_DIR, f"{certificate_id}.png")
    img.save(fp)
    return fp


def generate_certificate_pdf(
    student_name: str,
    domain_name:  str,
    start_date,
    end_date,
    issue_date,
    certificate_id: str,
    qr_code_path:   str,
    duration_text:  str = None,
) -> str:
    if not REPORTLAB_AVAILABLE:
        raise RuntimeError("Run: pip install reportlab")

    ensure_dirs()
    pdf_path = os.path.join(CERTIFICATES_DIR, f"{certificate_id}.pdf")

    W, H = landscape(A4)  # 841.89 × 595.28 pt
    c = rl_canvas.Canvas(pdf_path, pagesize=(W, H))

    # Color Palette
    TEXT_MAIN = HexColor('#0f172a')
    EXPOSYS_BLUE = HexColor('#1e40af')
    TEXT_SUBTLE = HexColor('#334155')

    CX = W / 2

    # 1. Background Image
    bg_path = os.path.join(_BASE, 'certificate_system', 'backend', 'certificate_template_blue.png')
    if os.path.exists(bg_path):
        c.drawImage(bg_path, 0, 0, width=W, height=H)
    else:
        # Fallback if image not found
        c.setFillColor(white)
        c.rect(0, 0, W, H, fill=1, stroke=0)

    # 2. Header
    Y = H - 90
    _center(c, "EXPOSYS DATA LABS", 'Helvetica-Bold', 18, EXPOSYS_BLUE, Y, W-100, W, charSpace=1.5)
    
    Y -= 50
    _center(c, "CERTIFICATE", 'Times-Bold', 42, EXPOSYS_BLUE, Y, W-100, W, charSpace=2)
    Y -= 30
    _center(c, "OF COMPLETION", 'Times-Bold', 28, EXPOSYS_BLUE, Y, W-100, W, charSpace=1)

    Y -= 50
    _center(c, "This certificate is proudly presented to", 'Helvetica', 16, TEXT_SUBTLE, Y, W-100, W)

    # 3. Student Name (Cursive/Italicized hero text)
    Y -= 70
    name_str = _tc(student_name)
    tw, _ = _center(c, name_str, 'Times-Italic', 46, EXPOSYS_BLUE, Y, W-200, W, charSpace=1)

    # Line under name
    Y -= 15
    line_w = max(tw + 80, 400)
    c.setStrokeColor(HexColor('#94a3b8'))
    c.setLineWidth(1)
    c.line(CX - line_w/2, Y, CX + line_w/2, Y)

    # 4. Paragraph Content (From Picture 1)
    Y -= 40
    if not duration_text:
        try:
            from datetime import datetime
            d1 = datetime.strptime(str(start_date), '%Y-%m-%d') if not isinstance(start_date, date) else start_date
            d2 = datetime.strptime(str(end_date), '%Y-%m-%d') if not isinstance(end_date, date) else end_date
            months = round((d2 - d1).days / 30.0)
            if months < 1: months = 1
            if months == 1:
                duration_text = "1 month"
            else:
                duration_text = f"{months} months"
        except:
            duration_text = "the specified period"
            
    start_fmt = _fmt(start_date)
    end_fmt = _fmt(end_date)
    
    from reportlab.platypus import Paragraph
    from reportlab.lib.styles import ParagraphStyle
    
    style = ParagraphStyle(
        name='Normal',
        fontName='Helvetica',
        fontSize=13,
        textColor=TEXT_SUBTLE,
        leading=18,
        alignment=1 # Center align
    )
    
    paragraph_text = f"For the Completing Internship with <b>Exposys Data Labs</b> under the domain <b>{domain_name}</b> of duration {duration_text} from {start_fmt} to {end_fmt}. During this Internship program, he/She demonstrated technical competence, problem-solving skills, and professionalism throughout the internship period."
    
    p = Paragraph(paragraph_text, style)
    p_width = W - 200
    p_height = p.wrap(p_width, H)[1]
    p.drawOn(c, 100, Y - p_height + 15)

    Y -= p_height + 25
    
    # ID and Date
    c.setFont('Helvetica', 12)
    c.setFillColor(TEXT_SUBTLE)
    c.drawString(CX - 100, Y, f"Unique id: [ {certificate_id} ]")
    c.drawString(CX - 100, Y - 20, f"Issued Date: [ {_fmt(issue_date)} ]")

    # 5. Footer (Signatures and Badge)
    FOOT_Y_LINE = 100
    
    # Left Signature
    SIG_L_X = 220
    c.setFont('Helvetica-Bold', 13)
    c.setFillColor(TEXT_MAIN)
    c.drawString(SIG_L_X - c.stringWidth("Vishnuvardhan y", 'Helvetica-Bold', 13)/2, FOOT_Y_LINE + 5, "Vishnuvardhan y")
    c.setStrokeColor(TEXT_SUBTLE)
    c.setLineWidth(0.5)
    c.line(SIG_L_X - 80, FOOT_Y_LINE - 5, SIG_L_X + 80, FOOT_Y_LINE - 5)
    c.setFont('Helvetica', 11)
    c.drawString(SIG_L_X - c.stringWidth("Chief Product Officer", 'Helvetica', 11)/2, FOOT_Y_LINE - 20, "Chief Product Officer")

    # Right Signature
    SIG_R_X = W - 220
    c.setFont('Helvetica-Bold', 13)
    c.setFillColor(TEXT_MAIN)
    c.drawString(SIG_R_X - c.stringWidth("Mothukuri Karthik", 'Helvetica-Bold', 13)/2, FOOT_Y_LINE + 5, "Mothukuri Karthik")
    c.setStrokeColor(TEXT_SUBTLE)
    c.setLineWidth(0.5)
    c.line(SIG_R_X - 80, FOOT_Y_LINE - 5, SIG_R_X + 80, FOOT_Y_LINE - 5)
    c.setFont('Helvetica', 11)
    c.drawString(SIG_R_X - c.stringWidth("Chief Operation Manager", 'Helvetica', 11)/2, FOOT_Y_LINE - 20, "Chief Operation Manager")

    # Center QR Code / Badge
    if qr_code_path and os.path.exists(qr_code_path):
        QR_SIZE = 75
        QR_X = CX
        QR_Y = FOOT_Y_LINE - 30
        c.drawImage(qr_code_path, QR_X - QR_SIZE/2, QR_Y, width=QR_SIZE, height=QR_SIZE, preserveAspectRatio=True)

    c.save()
    return pdf_path

def compute_blockchain_hash(meta: dict) -> str:
    import json
    raw = json.dumps(meta, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()
