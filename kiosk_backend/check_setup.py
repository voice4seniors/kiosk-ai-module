#!/usr/bin/env python3
"""
키오스크 백엔드 환경 검증 스크립트
설치 및 설정 상태를 체크하고 문제점을 진단합니다.
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Python 버전 확인"""
    print("🐍 Python 환경 검사")
    print("-" * 30)
    
    version = sys.version_info
    print(f"Python 버전: {version.major}.{version.minor}.{version.micro}")
    
    if version.major != 3:
        print("❌ Python 3이 필요합니다.")
        return False
    elif version.minor < 8:
        print("⚠️  Python 3.8 이상을 권장합니다.")
        return True
    elif version.minor > 11:
        print("⚠️  Python 3.12는 일부 패키지와 호환성 문제가 있을 수 있습니다.")
        return True
    else:
        print("✅ Python 버전이 적절합니다.")
        return True

def check_packages():
    """필수 패키지 설치 확인"""
    print("\n📦 패키지 설치 상태")
    print("-" * 30)
    
    required_packages = [
        ('fastapi', 'FastAPI 웹 프레임워크'),
        ('uvicorn', 'ASGI 서버'),
        ('whisper', 'OpenAI Whisper 음성인식'),
        ('torch', 'PyTorch 딥러닝 프레임워크'),
        ('sklearn', 'Scikit-learn 머신러닝'),
        ('pandas', 'Pandas 데이터 처리'),
        ('numpy', 'NumPy 수치 연산'),
        ('joblib', 'Joblib 모델 저장/로드'),
        ('pydantic', 'Pydantic 데이터 검증'),
    ]
    
    all_installed = True
    
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"✅ {package:12} - {description}")
        except ImportError:
            print(f"❌ {package:12} - {description} (설치 필요)")
            all_installed = False
    
    return all_installed

def check_model_files():
    """AI 모델 파일 확인"""
    print("\n🤖 AI 모델 파일 확인")
    print("-" * 30)
    
    possible_paths = [
        "../ai_module",
        "./ai_module", 
        "ai_module"
    ]
    
    model_files = ["intent_model.pkl", "vectorizer.pkl"]
    found_models = False
    
    for ai_path in possible_paths:
        if os.path.exists(ai_path):
            print(f"📁 {ai_path} 디렉토리 발견")
            for model_file in model_files:
                full_path = os.path.join(ai_path, model_file)
                if os.path.exists(full_path):
                    size = os.path.getsize(full_path)
                    print(f"  ✅ {model_file} ({size:,} bytes)")
                    found_models = True
                else:
                    print(f"  ❌ {model_file}")
    
    if not found_models:
        print("⚠️  AI 모델 파일이 없습니다.")
        print("💡 데모 모드로 실행 가능 (키워드 기반 분류)")
    else:
        print("✅ AI 모델이 준비되었습니다.")
    
    return found_models

def check_ports():
    """포트 사용 현황 확인"""
    print("\n🔌 포트 확인")
    print("-" * 30)
    
    try:
        import socket
        
        # 8000 포트 확인
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8000))
        
        if result == 0:
            print("⚠️  포트 8000이 이미 사용 중입니다.")
            print("   다른 서버가 실행 중일 수 있습니다.")
        else:
            print("✅ 포트 8000 사용 가능")
        
        sock.close()
        
    except Exception as e:
        print(f"❌ 포트 확인 중 오류: {e}")

def check_directory_structure():
    """디렉토리 구조 확인"""
    print("\n📁 디렉토리 구조")
    print("-" * 30)
    
    current_dir = Path.cwd()
    print(f"현재 위치: {current_dir}")
    
    expected_files = [
        "main.py",
        "run_server.py", 
        "test_client.py",
        "config.py",
        "requirements.txt"
    ]
    
    for file in expected_files:
        if (current_dir / file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")

def run_quick_test():
    """빠른 import 테스트"""
    print("\n🧪 빠른 테스트")
    print("-" * 30)
    
    try:
        from main import app
        print("✅ main.py 로드 성공")
    except Exception as e:
        print(f"❌ main.py 로드 실패: {e}")
        return False
    
    try:
        import whisper
        model = whisper.load_model("tiny")
        print("✅ Whisper 모델 로드 성공")
    except Exception as e:
        print(f"⚠️  Whisper 모델 로드 실패: {e}")
    
    return True

def main():
    """메인 검증 함수"""
    print("=" * 50)
    print("🚀 키오스크 백엔드 환경 검증")
    print("=" * 50)
    
    checks = [
        ("Python 버전", check_python_version()),
        ("패키지 설치", check_packages()),
        ("모델 파일", check_model_files()),
        ("디렉토리 구조", check_directory_structure()),
    ]
    
    check_ports()
    
    print("\n" + "=" * 50)
    print("📋 검증 결과 요약")
    print("=" * 50)
    
    passed = 0
    for name, result in checks:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{name:15}: {status}")
        if result:
            passed += 1
    
    print(f"\n통과율: {passed}/{len(checks)} ({passed/len(checks)*100:.0f}%)")
    
    if passed >= 3:  # 최소 3개 이상 통과
        print("\n🎉 서버 실행 준비 완료!")
        print("다음 명령으로 서버를 시작하세요:")
        print("  python run_server.py")
        
        run_quick_test()
    else:
        print("\n⚠️  추가 설정이 필요합니다.")
        print("requirements.txt로 패키지를 먼저 설치해주세요:")
        print("  pip install -r requirements.txt")

if __name__ == "__main__":
    main()