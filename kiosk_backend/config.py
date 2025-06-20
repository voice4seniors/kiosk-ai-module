import os
from pathlib import Path

class Config:
    """애플리케이션 설정"""
    
    # 서버 설정
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # AI 모델 경로
    AI_MODULE_PATH = os.getenv("AI_MODULE_PATH", "../ai_module")
    INTENT_MODEL_PATH = os.path.join(AI_MODULE_PATH, "intent_model.pkl")
    VECTORIZER_PATH = os.path.join(AI_MODULE_PATH, "vectorizer.pkl")
    
    # Whisper 설정
    WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "tiny")  # tiny, base, small, medium, large
    
    # 파일 업로드 설정
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))  # 10MB
    ALLOWED_AUDIO_FORMATS = ["audio/wav", "audio/mp3", "audio/m4a", "audio/ogg"]
    
    # 의도 분류 설정
    CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", 0.5))
    
    # 로깅 설정
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # CORS 설정
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # 의도 매핑
    INTENT_MAPPING = {
        0: "증명서 발급",
        1: "주소 변경", 
        2: "여권 발급",
        3: "직원 호출",
        4: "시작화면"
    }
    
    # 의도별 상세 정보
    INTENT_DETAILS = {
        0: {
            "name": "증명서 발급",
            "description": "주민등록등본, 초본 등 각종 증명서 발급",
            "required_documents": ["신분증"],
            "estimated_time": "5-10분",
            "fee": "1,000원"
        },
        1: {
            "name": "주소 변경",
            "description": "전입신고, 전출신고 등 주소 변경 업무",
            "required_documents": ["신분증", "전입신고서"],
            "estimated_time": "10-15분",
            "fee": "무료"
        },
        2: {
            "name": "여권 발급",
            "description": "신규 여권 발급 및 재발급",
            "required_documents": ["신분증", "여권용 사진", "신청서"],
            "estimated_time": "20-30분",
            "fee": "53,000원"
        },
        3: {
            "name": "직원 호출",
            "description": "담당 직원 호출 및 상담 요청",
            "required_documents": [],
            "estimated_time": "즉시",
            "fee": "무료"
        },
        4: {
            "name": "시작화면",
            "description": "메인 화면으로 돌아가기",
            "required_documents": [],
            "estimated_time": "즉시",
            "fee": "무료"
        }
    }

class DevelopmentConfig(Config):
    """개발 환경 설정"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"

class ProductionConfig(Config):
    """운영 환경 설정"""
    DEBUG = False
    LOG_LEVEL = "WARNING"
    CORS_ORIGINS = ["https://yourdomain.com"]  # 실제 도메인으로 변경

# 환경에 따른 설정 선택
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}

def get_config():
    """현재 환경에 맞는 설정 반환"""
    env = os.getenv("ENVIRONMENT", "default")
    return config.get(env, config["default"])