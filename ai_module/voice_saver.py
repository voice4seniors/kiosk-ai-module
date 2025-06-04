import sounddevice as sd
import soundfile as sf

def record_audio(filename="kiosk_input.wav", duration=5, samplerate=16000):
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
    sd.wait()  # 녹음이 끝날 때까지 대기
    sf.write(filename, audio, samplerate)

record_audio(duration=5)
