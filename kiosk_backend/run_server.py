import uvicorn
import os
import sys
from pathlib import Path

def main():
    """서버 실행"""
    
    # AI 모델 파일 경로 확인
    ai_module_path = Path("../ai_module")
    model_files = ["intent_model.pkl", "vectorizer.pkl"]
    
    print("=== 어르신 음성인식 AI 키오스크 백엔드 서버 ===")
    print()
    
    # AI 모델 파일 존재 확인
    missing_files = []
    for file in model_files:
        file_path = ai_module_path / file
        if file_path.exists():
            print(f"✓ {file} 발견")
        else:
            print(f"✗ {file} 없음")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n⚠️  누락된 모델 파일: {missing_files}")
        print("💡 AI 모듈이 없어도 데모 모드로 실행 가능합니다.")
        print("📋 키워드 기반 의도 분류가 동작합니다.")
        
        user_input = input("\n계속 진행하시겠습니까? (y/n): ")
        if user_input.lower() != 'y':
            print("서버 실행을 취소합니다.")
            return
    
    print("\n🚀 서버를 시작합니다...")
    print("📋 API 문서: http://localhost:8000/docs")
    print("🔍 헬스 체크: http://localhost:8000/health")
    print("\n중단하려면 Ctrl+C를 누르세요.\n")
    
    # 서버 실행
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()