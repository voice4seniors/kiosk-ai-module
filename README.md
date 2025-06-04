# kiosk-ai-module
AI 모듈 레포지토리입니다

---

- dataset.ipynb → 데이터 셋 만들기(5개의 의도, 각각 문장 150개 -> 총 750개)
- intent_dataset.csv → 위 코드로 만들어진 csv 데이터 셋
- save_voice.ipynb → whisper로 음성 인식하기 위해서 음성 저장
- whisper.ipynb → whisper 연동(STT - 음성 파일 텍스트로 변환)
- model.ipynb → 의도 분류를 위한 모델학습, 테스트

## 📂 ai_module (ipynb 파일을 py파일로 변환)
- pkl 파일 → intent_predictor.py에서 clf, vectorizer 로드하기 위한 파일
- intent_predictor.py → 학습된 모델로 의도 분류
- voice_saver.py → 음성 녹음 및 저장
- whisper_infer.py → whisper로 음성 텍스트로 변환

## 🔗 intent 설명
- 0 - 증명서 발급: 주민등록등본
- 1 - 주소 변경: 전입신고, 전출신고
- 2 - 여권 발급: 여권 발급하기
- 3 - 직원 호출: 직원 부르기
- 4 - 시작화면: 처음으로 돌아가기
