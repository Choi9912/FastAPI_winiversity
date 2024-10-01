from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os


# 프로젝트 루트 디렉토리 경로를 가져옵니다.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def generate_certificate_pdf(certificate, user, db):
    # 폰트 파일의 절대 경로를 지정합니다.
    font_path = os.path.join(BASE_DIR, "app", "assets", "fonts", "NanumGothic.ttf")

    # 폰트를 등록합니다.
    pdfmetrics.registerFont(TTFont("NanumGothic", font_path))

    # PDF 생성 로직
    filename = f"certificate_{certificate.certificate_number}.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("NanumGothic", 12)

    # 여기에 PDF 내용 생성 로직을 추가하세요.
    c.drawString(100, 750, f"Certificate Number: {certificate.certificate_number}")
    c.drawString(100, 710, f"Issue Date: {certificate.issue_date}")

    c.save()

    return filename
