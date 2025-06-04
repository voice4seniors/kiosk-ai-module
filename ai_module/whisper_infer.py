import whisper

model = whisper.load_model("tiny")
result = model.transcribe("kiosk_input.wav")
# result["text"]