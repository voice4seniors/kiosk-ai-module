from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import whisper
import joblib
import os
import tempfile
import logging
from typing import Dict, Any
import uvicorn
from pydantic import BaseModel

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="어르신 음성인식 AI 키오스크",
    description="음성 인식을 통한 민원 업무 처리 키오스크 백엔드",
    version="1.0.0"
)

# CORS 설정 (프론트엔드와 연동을 위해)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포시에는 구체적인 도메인으로 변경
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 변수로 모델들 저장
whisper_model = None
intent_classifier = None
vectorizer = None

# 의도 매핑
INTENT_MAPPING = {
    0: "증명서 발급",
    1: "주소 변경", 
    2: "여권 발급",
    3: "직원 호출",
    4: "시작화면"
}

# 요청/응답 모델
class TextRequest(BaseModel):
    text: str

class VoiceResponse(BaseModel):
    success: bool
    transcribed_text: str
    predicted_intent: int
    intent_description: str
    confidence: float
    message: str

class IntentResponse(BaseModel):
    success: bool
    predicted_intent: int
    intent_description: str
    confidence: float
    message: str

@app.on_event("startup")
async def startup_event():
    """서버 시작시 AI 모델들 로드"""
    global whisper_model, intent_classifier, vectorizer
    
    try:
        # Whisper 모델 로드
        logger.info("Whisper 모델 로드 중...")
        whisper_model = whisper.load_model("tiny")
        logger.info("Whisper 모델 로드 완료")
        
        # 의도 분류 모델 및 벡터라이저 로드
        logger.info("의도 분류 모델 로드 중...")
        
        # AI 모듈 경로 (여러 경로 시도)
        possible_paths = [
            "../ai_module",  # 상위 디렉토리
            "./ai_module",   # 현재 디렉토리
            "ai_module",     # 하위 디렉토리
            os.path.join(os.path.dirname(__file__), "../ai_module"),  # 절대 경로
        ]
        
        ai_module_path = None
        for path in possible_paths:
            if os.path.exists(f"{path}/intent_model.pkl") and os.path.exists(f"{path}/vectorizer.pkl"):
                ai_module_path = path
                logger.info(f"AI 모듈 경로 찾음: {ai_module_path}")
                break
        
        if ai_module_path is None:
            logger.warning("AI 모델 파일들을 찾을 수 없습니다.")
            logger.warning("다음 경로들을 확인했습니다:")
            for path in possible_paths:
                logger.warning(f"  - {path}")
            logger.warning("데모 모드로 실행됩니다.")
            return  # 오류를 발생시키지 않고 데모 모드로 계속 실행
        
        intent_classifier = joblib.load(f"{ai_module_path}/intent_model.pkl")
        vectorizer = joblib.load(f"{ai_module_path}/vectorizer.pkl")
        logger.info("의도 분류 모델 로드 완료")
        
    except Exception as e:
        logger.error(f"모델 로드 실패: {e}")
        logger.warning("데모 모드로 실행됩니다. (실제 모델 없이 목업 응답)")
        # 시연용으로 모델 로드 실패해도 서버는 계속 실행되도록 함

def predict_intent_with_confidence(text: str) -> tuple:
    """텍스트에서 의도 예측 및 신뢰도 반환"""
    try:
        # 모델이 로드되지 않은 경우 데모 응답
        if intent_classifier is None or vectorizer is None:
            logger.warning("모델이 로드되지 않아 데모 응답을 반환합니다.")
            return get_demo_intent_response(text)
        
        # 텍스트 벡터화
        text_vec = vectorizer.transform([text])
        
        # 의도 예측
        predicted_intent = intent_classifier.predict(text_vec)[0]
        
        # 신뢰도 계산 (확률의 최댓값)
        probabilities = intent_classifier.predict_proba(text_vec)[0]
        confidence = float(max(probabilities))
        
        return predicted_intent, confidence
        
    except Exception as e:
        logger.error(f"의도 예측 실패: {e}")
        return get_demo_intent_response(text)

def get_demo_intent_response(text: str) -> tuple:
    """데모용 의도 응답 (모델 없이도 시연 가능)"""
    text_lower = text.lower()
    
    # 키워드 기반 간단한 분류
    if any(keyword in text_lower for keyword in ["등본", "증명서", "발급", "뽑"]):
        return 0, 0.95  # 증명서 발급
    elif any(keyword in text_lower for keyword in ["주소", "전입", "전출", "이사"]):
        return 1, 0.92  # 주소 변경
    elif any(keyword in text_lower for keyword in ["여권", "passport"]):
        return 2, 0.88  # 여권 발급
    elif any(keyword in text_lower for keyword in ["직원", "사람", "호출", "불러", "도움"]):
        return 3, 0.90  # 직원 호출
    elif any(keyword in text_lower for keyword in ["처음", "시작", "홈", "메인", "돌아"]):
        return 4, 0.85  # 시작화면
    else:
        return 0, 0.60  # 기본값: 증명서 발급

@app.get("/")
def root():
    """서버 상태 확인"""
    return {
        "message": "어르신 음성인식 AI 키오스크 백엔드가 실행 중입니다.",
        "status": "running",
        "whisper_loaded": whisper_model is not None,
        "intent_model_loaded": intent_classifier is not None
    }

@app.get("/health")
def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "models_loaded": {
            "whisper": whisper_model is not None,
            "intent_classifier": intent_classifier is not None,
            "vectorizer": vectorizer is not None
        }
    }

@app.post("/voice-to-intent", response_model=VoiceResponse)
async def voice_to_intent(audio: UploadFile = File(...)):
    """음성 파일을 받아서 텍스트 변환 후 의도 분류"""
    
    try:
        # 업로드된 파일 검증
        if not audio.content_type or not audio.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="오디오 파일만 업로드 가능합니다.")
        
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await audio.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Whisper 모델이 없는 경우 데모 응답
            if whisper_model is None:
                logger.warning("Whisper 모델이 없어 데모 응답을 반환합니다.")
                demo_texts = [
                    "주민등록등본 발급해주세요",
                    "전입신고 하러 왔어요", 
                    "여권 만들고 싶어요",
                    "직원 좀 불러주세요",
                    "처음으로 돌아가고 싶어요"
                ]
                import random
                transcribed_text = random.choice(demo_texts)
            else:
                # Whisper로 음성을 텍스트로 변환
                logger.info("음성 인식 시작...")
                result = whisper_model.transcribe(temp_file_path)
                transcribed_text = result["text"].strip()
                logger.info(f"음성 인식 결과: {transcribed_text}")
            
            if not transcribed_text:
                return VoiceResponse(
                    success=False,
                    transcribed_text="",
                    predicted_intent=-1,
                    intent_description="인식 실패",
                    confidence=0.0,
                    message="음성을 인식할 수 없습니다. 다시 말씀해 주세요."
                )
            
            # 의도 분류
            predicted_intent, confidence = predict_intent_with_confidence(transcribed_text)
            intent_description = INTENT_MAPPING.get(predicted_intent, "알 수 없음")
            
            logger.info(f"예측된 의도: {intent_description} (신뢰도: {confidence:.2f})")
            
            return VoiceResponse(
                success=True,
                transcribed_text=transcribed_text,
                predicted_intent=predicted_intent,
                intent_description=intent_description,
                confidence=confidence,
                message=f"'{transcribed_text}' → {intent_description}"
            )
            
        finally:
            # 임시 파일 삭제
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            
    except Exception as e:
        logger.error(f"음성 처리 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=f"음성 처리 중 오류가 발생했습니다: {str(e)}")

@app.post("/text-to-intent", response_model=IntentResponse)
async def text_to_intent(request: TextRequest):
    """텍스트에서 의도 분류"""
    
    try:
        text = request.text.strip()
        
        if not text:
            raise HTTPException(status_code=400, detail="텍스트가 비어있습니다.")
        
        # 의도 분류
        predicted_intent, confidence = predict_intent_with_confidence(text)
        intent_description = INTENT_MAPPING.get(predicted_intent, "알 수 없음")
        
        logger.info(f"텍스트: '{text}' → 의도: {intent_description} (신뢰도: {confidence:.2f})")
        
        return IntentResponse(
            success=True,
            predicted_intent=predicted_intent,
            intent_description=intent_description,
            confidence=confidence,
            message=f"'{text}' → {intent_description}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"텍스트 처리 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=f"텍스트 처리 중 오류가 발생했습니다: {str(e)}")

@app.get("/intents")
def get_intents():
    """사용 가능한 의도 목록 반환"""
    return {
        "intents": INTENT_MAPPING,
        "count": len(INTENT_MAPPING)
    }

@app.post("/process-intent/{intent_id}")
def process_intent(intent_id: int):
    """특정 의도에 대한 처리 로직"""
    
    if intent_id not in INTENT_MAPPING:
        raise HTTPException(status_code=400, detail="유효하지 않은 의도 ID입니다.")
    
    intent_description = INTENT_MAPPING[intent_id]
    
    # 의도별 처리 로직
    response_data = {
        "intent_id": intent_id,
        "intent_description": intent_description,
        "status": "처리 완료"
    }
    
    if intent_id == 0:  # 증명서 발급
        response_data.update({
            "action": "certificate_issue",
            "next_steps": ["본인 확인", "발급 유형 선택", "수수료 결제"],
            "message": "주민등록등본 발급을 위해 본인 확인이 필요합니다."
        })
    
    elif intent_id == 1:  # 주소 변경
        response_data.update({
            "action": "address_change", 
            "next_steps": ["전입/전출 구분", "신규 주소 입력", "서류 제출"],
            "message": "주소 변경 신고를 진행하겠습니다."
        })
    
    elif intent_id == 2:  # 여권 발급
        response_data.update({
            "action": "passport_issue",
            "next_steps": ["신청서 작성", "사진 촬영", "수수료 결제"],
            "message": "여권 발급 신청을 시작합니다."
        })
    
    elif intent_id == 3:  # 직원 호출
        response_data.update({
            "action": "call_staff",
            "next_steps": ["직원 호출 중"],
            "message": "직원을 호출하고 있습니다. 잠시만 기다려 주세요."
        })
    
    elif intent_id == 4:  # 시작화면
        response_data.update({
            "action": "goto_home",
            "next_steps": ["메인 화면으로 이동"],
            "message": "처음 화면으로 돌아갑니다."
        })
    
    return response_data

@app.get("/demo/examples")
def get_demo_examples():
    """시연용 예제 문장들"""
    return {
        "voice_examples": [
            {"text": "주민등록등본 발급해주세요", "expected_intent": 0},
            {"text": "전입신고 하러 왔어요", "expected_intent": 1},
            {"text": "여권 만들고 싶어요", "expected_intent": 2},
            {"text": "직원 좀 불러주세요", "expected_intent": 3},
            {"text": "처음으로 돌아가고 싶어요", "expected_intent": 4}
        ],
        "usage_tip": "위 예제 문장들을 음성으로 말하거나 텍스트로 입력해보세요."
    }

@app.post("/demo/simulate-voice")
async def simulate_voice_input():
    """시연용 음성 입력 시뮬레이션"""
    import random
    
    demo_scenarios = [
        {
            "transcribed_text": "주민등록등본 발급해주세요",
            "predicted_intent": 0,
            "intent_description": "증명서 발급",
            "confidence": 0.95
        },
        {
            "transcribed_text": "전입신고 하러 왔어요",
            "predicted_intent": 1,
            "intent_description": "주소 변경",
            "confidence": 0.92
        },
        {
            "transcribed_text": "여권 만들고 싶어요",
            "predicted_intent": 2,
            "intent_description": "여권 발급",
            "confidence": 0.88
        }
    ]
    
    scenario = random.choice(demo_scenarios)
    
    return VoiceResponse(
        success=True,
        transcribed_text=scenario["transcribed_text"],
        predicted_intent=scenario["predicted_intent"],
        intent_description=scenario["intent_description"],
        confidence=scenario["confidence"],
        message=f"[시연용] '{scenario['transcribed_text']}' → {scenario['intent_description']}"
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )