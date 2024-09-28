# 예시 헬퍼 함수
def format_response(data: dict, message: str = "성공"):
    return {"status": "success", "message": message, "data": data}
