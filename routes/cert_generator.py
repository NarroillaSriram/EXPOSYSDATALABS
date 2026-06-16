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

    # ── Happy, Peaceful Blue Color Palette ─────────────────────────────────
    BG_COLOR = HexColor('#F0F8FF')       # Soft Alice Blue (very peaceful and happy)
    SOFT_SLATE = HexColor('#94A3B8')     # Peaceful gentle border color
    MUTED_GOLD = HexColor('#D4AF37')     # Elegant gold for inner accent
    TEXT_MAIN = HexColor('#1E293B')      # Deep slate for main text
    TEXT_SUBTLE = HexColor('#475569')    # Subtle grey for reading text
    DARK_BLUE = HexColor('#0F172A')      # Very deep dark blue/navy
    EXPOSYS_BLUE = HexColor('#1D4ED8')   # Highlight dark blue for Exposys

    CX = W / 2

    # 1. Background Fill
    c.setFillColor(BG_COLOR)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # 2. Peaceful Rounded Borders
    # Outer border (Soft Dark Blue)
    M_OUT = 40
    c.setStrokeColor(DARK_BLUE)
    c.setLineWidth(1.5)
    c.roundRect(M_OUT, M_OUT, W - 2*M_OUT, H - 2*M_OUT, radius=25, stroke=1, fill=0)

    # Inner border (Muted Gold)
    M_IN = 50
    c.setStrokeColor(MUTED_GOLD)
    c.setLineWidth(0.8)
    c.roundRect(M_IN, M_IN, W - 2*M_IN, H - 2*M_IN, radius=20, stroke=1, fill=0)

    # 3. Soft Header (Exposys highlighted in Dark Blue)
    Y = H - 120
    _center(c, "E X P O S Y S   D A T A   L A B S", 'Helvetica-Bold', 18, EXPOSYS_BLUE, Y, W-100, W, charSpace=1.5)
    
    Y -= 15
    c.setStrokeColor(MUTED_GOLD)
    c.setLineWidth(1)
    c.line(CX - 40, Y + 6, CX + 40, Y + 6)
    
    # 4. Certificate Title
    Y -= 55
    _center(c, "CERTIFICATE OF COMPLETION", 'Times-Bold', 40, DARK_BLUE, Y, W-100, W)

    Y -= 40
    _center(c, "This certificate is proudly awarded to", 'Times-Italic', 18, TEXT_SUBTLE, Y, W-100, W)

    # 5. Student Name (Hero Element)
    Y -= 75
    name_str = _tc(student_name)
    tw, _ = _center(c, name_str, 'Helvetica-Bold', 42, EXPOSYS_BLUE, Y, W-200, W, charSpace=1)

    # Very delicate line under name
    Y -= 20
    line_w = max(tw + 80, 350)
    c.setStrokeColor(SOFT_SLATE)
    c.setLineWidth(0.5)
    c.line(CX - line_w/2, Y, CX + line_w/2, Y)

    # 6. Description & Domain (Standard professional wording)
    Y -= 40
    _center(c, "for successfully completing the internship program in", 'Times-Italic', 16, TEXT_SUBTLE, Y, W-100, W)

    Y -= 40
    _center(c, domain_name, 'Times-Bold', 22, DARK_BLUE, Y, W-100, W, charSpace=0.5)

    Y -= 35
    if not duration_text:
        try:
            from datetime import datetime
            d1 = datetime.strptime(str(start_date), '%Y-%m-%d') if not isinstance(start_date, date) else start_date
            d2 = datetime.strptime(str(end_date), '%Y-%m-%d') if not isinstance(end_date, date) else end_date
            months = round((d2 - d1).days / 30.0)
            if months < 1: months = 1
            duration_text = f"{months} Month{'s' if months > 1 else ''}"
        except:
            duration_text = "the specified period"

    dur_str = f"for a duration of {duration_text}."
    _center(c, dur_str, 'Helvetica', 14, TEXT_SUBTLE, Y, W-100, W)

    # 7. Peaceful, perfectly balanced footer
    FOOT_Y_LINE = 110
    
    # Left: Date
    DATE_X = 180
    c.setFont('Times-Bold', 14)
    c.setFillColor(DARK_BLUE)
    date_text = _fmt(issue_date)
    c.drawString(DATE_X - c.stringWidth(date_text, 'Times-Bold', 14)/2, FOOT_Y_LINE + 5, date_text)
    
    c.setStrokeColor(SOFT_SLATE)
    c.setLineWidth(0.5)
    c.line(DATE_X - 50, FOOT_Y_LINE - 5, DATE_X + 50, FOOT_Y_LINE - 5)
    
    c.setFont('Helvetica', 9)
    c.setFillColor(TEXT_SUBTLE)
    c.drawString(DATE_X - c.stringWidth("Date of Issue", 'Helvetica', 9)/2, FOOT_Y_LINE - 20, "Date of Issue")

    # Center: Signature
    SIG_X = CX
    c.setFont('Times-BoldItalic', 20)
    c.setFillColor(EXPOSYS_BLUE)
    sig_name = "Vishnuvardhan Y"
    c.drawString(SIG_X - c.stringWidth(sig_name, 'Times-BoldItalic', 20)/2, FOOT_Y_LINE + 5, sig_name)
    
    c.setStrokeColor(SOFT_SLATE)
    c.setLineWidth(0.5)
    c.line(SIG_X - 70, FOOT_Y_LINE - 5, SIG_X + 70, FOOT_Y_LINE - 5)
    
    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(DARK_BLUE)
    title_text = "Chief Product Officer"
    c.drawString(SIG_X - c.stringWidth(title_text, 'Helvetica-Bold', 9)/2, FOOT_Y_LINE - 20, title_text)

    # Right: Clean, Soft QR Code Integration
    if qr_code_path and os.path.exists(qr_code_path):
        QR_SIZE = 60
        QR_X = W - 180
        QR_Y = FOOT_Y_LINE - 25
        c.drawImage(qr_code_path, QR_X - QR_SIZE/2, QR_Y, width=QR_SIZE, height=QR_SIZE, preserveAspectRatio=True)
        
        c.setFont('Helvetica', 7)
        c.setFillColor(TEXT_SUBTLE)
        id_text = f"ID: {certificate_id}"
        c.drawString(QR_X - c.stringWidth(id_text, 'Helvetica', 7)/2, QR_Y - 12, id_text)

    c.save()
    return pdf_path

def compute_blockchain_hash(meta: dict) -> str:
    import json
    raw = json.dumps(meta, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()
