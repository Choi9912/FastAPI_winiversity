from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import os
from datetime import datetime

# 프로젝트 루트 디렉토리 경로를 가져옵니다.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def generate_certificate_pdf(certificate, user, course, db):
    # 폰트 파일의 절대 경로를 지정합니다.
    font_path = os.path.join(BASE_DIR, "app", "assets", "fonts", "NanumGothic.ttf")
    bold_font_path = os.path.join(
        BASE_DIR, "app", "assets", "fonts", "NanumGothicBold.ttf"
    )

    # 폰트를 등록합니다.
    pdfmetrics.registerFont(TTFont("NanumGothic", font_path))
    pdfmetrics.registerFont(TTFont("NanumGothicBold", bold_font_path))

    # PDF 생성 로직
    filename = f"certificate_{certificate.certificate_number}.pdf"
    c = canvas.Canvas(filename, pagesize=landscape(letter))
    width, height = landscape(letter)

    # 배경 색상 설정
    c.setFillColor(HexColor("#F0F0F0"))
    c.rect(0, 0, width, height, fill=1)

    # 제목
    c.setFont("NanumGothicBold", 36)
    c.setFillColor(HexColor("#333333"))
    c.drawCentredString(width / 2, height - 2 * inch, "수료증")

    # 내용
    c.setFont("NanumGothic", 14)
    c.setFillColor(HexColor("#555555"))

    # 사용자 이름
    user_name = user.nickname or user.username
    c.drawCentredString(width / 2, height - 3.5 * inch, f"이름: {user_name}")

    # 코스 제목
    c.drawCentredString(width / 2, height - 4 * inch, f"과정명: {course.title}")

    # 수료 날짜
    issue_date = certificate.issue_date.strftime("%Y년 %m월 %d일")
    c.drawCentredString(width / 2, height - 4.5 * inch, f"수료일: {issue_date}")

    # 인증 번호
    c.setFont("NanumGothic", 10)
    c.drawString(1 * inch, 1 * inch, f"인증번호: {certificate.certificate_number}")

    # 서명 라인
    c.line(width / 2 - 2 * inch, 2 * inch, width / 2 + 2 * inch, 2 * inch)
    c.drawCentredString(width / 2, 1.7 * inch, "서명")

    # 현재 날짜
    current_date = datetime.now().strftime("%Y년 %m월 %d일")
    c.drawCentredString(width / 2, 1.3 * inch, f"발급일: {current_date}")

    c.save()

    return filename
