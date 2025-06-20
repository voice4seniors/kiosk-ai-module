import requests
import json
from pathlib import Path

# 서버 URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """헬스 체크 테스트"""
    print("=== 헬스 체크 테스트 ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_text_to_intent():
    """텍스트 의도 분류 테스트"""
    print("=== 텍스트 의도 분류 테스트 ===")
    
    test_texts = [
        "주민등록등본 발급해주세요",
        "전입신고 하러 왔어요", 
        "여권 만들고 싶어요",
        "직원 좀 불러주세요",
        "처음으로 돌아가고 싶어요"
    ]
    
    for text in test_texts:
        response = requests.post(
            f"{BASE_URL}/text-to-intent",
            json={"text": text}
        )
        print(f"텍스트: '{text}'")
        print(f"응답: {response.json()}")
        print("-" * 50)

def test_voice_to_intent(audio_file_path):
    """음성 의도 분류 테스트"""
    print("=== 음성 의도 분류 테스트 ===")
    
    if not Path(audio_file_path).exists():
        print(f"오디오 파일을 찾을 수 없습니다: {audio_file_path}")
        return
    
    with open(audio_file_path, "rb") as audio_file:
        files = {"audio": ("test.wav", audio_file, "audio/wav")}
        response = requests.post(f"{BASE_URL}/voice-to-intent", files=files)
        
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_get_intents():
    """의도 목록 조회 테스트"""
    print("=== 의도 목록 조회 테스트 ===")
    response = requests.get(f"{BASE_URL}/intents")
    print(f"Response: {response.json()}")
    print()

def test_process_intent():
    """의도 처리 테스트"""
    print("=== 의도 처리 테스트 ===")
    
    for intent_id in range(5):
        response = requests.post(f"{BASE_URL}/process-intent/{intent_id}")
        print(f"Intent ID {intent_id}:")
        print(f"Response: {response.json()}")
        print("-" * 50)

if __name__ == "__main__":
    try:
        # 서버 연결 확인
        test_health_check()
        
        # 각종 기능 테스트
        test_get_intents()
        test_text_to_intent()
        test_process_intent()
        
        # 음성 파일이 있다면 테스트
        # test_voice_to_intent("../ai_module/kiosk_input.wav")
        
    except requests.exceptions.ConnectionError:
        print("서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.")
    except Exception as e:
        print(f"테스트 중 오류 발생: {e}")