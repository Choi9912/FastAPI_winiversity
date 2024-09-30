from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os


def generate_certificate_pdf(certificate, user, db):
    # 폰트 등록 (한글 지원을 위해)
    pdfmetrics.registerFont(TTFont("NanumGothic", "NanumGothic.ttf"))

    # PDF 생성
    filename = f"certificate_{certificate.certificate_number}.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # 제목
    c.setFont("NanumGothic", 30)
    c.drawCentredString(width / 2, height - 100, "수료증")

    # 내용
    c.setFont("NanumGothic", 16)
    c.drawCentredString(width / 2, height - 150, f"이름: {user.username}")
    c.drawCentredString(width / 2, height - 180, f"과목: {certificate.course.title}")
    c.drawCentredString(
        width / 2,
        height - 210,
        f"수료일: {certificate.issue_date.strftime('%Y-%m-%d')}",
    )
    c.drawCentredString(
        width / 2, height - 240, f"인증번호: {certificate.certificate_number}"
    )

    c.save()

    # 파일 경로 저장 (예: 데이터베이스에 저장)
    certificate.pdf_path = os.path.abspath(filename)
    db.commit()
