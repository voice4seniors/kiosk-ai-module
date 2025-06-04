import IPython
from IPython.display import Audio, display, Javascript
from base64 import b64decode

def record_audio(filename="kiosk_input.wav", duration=5):
    js = Javascript("""
    const sleep = time => new Promise(resolve => setTimeout(resolve, time))

    const record = async () => {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        let audioChunks = [];

        mediaRecorder.ondataavailable = event => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };

        mediaRecorder.start();

        await sleep(1000 * %d);

        mediaRecorder.stop();

        await new Promise(resolve => mediaRecorder.onstop = resolve);

        const audioBlob = new Blob(audioChunks);
        const reader = new FileReader();
        reader.readAsDataURL(audioBlob);
        reader.onloadend = () => {
            const base64AudioMessage = reader.result.split(',')[1];
            google.colab.kernel.invokeFunction('notebook.receiveKioskOrder', [base64AudioMessage], {});
        };
    };

    record();
    """ % duration)

    display(js)

from google.colab import output
import io
import soundfile as sf

def receive_audio(audio_base64):
    audio_bytes = b64decode(audio_base64)
    with open("kiosk_input.wav", "wb") as f:
        f.write(audio_bytes)
#    print("녹음 완료: kiosk_input.wav")

output.register_callback('notebook.receiveKioskOrder', receive_audio)

record_audio(duration=5)  # 5초 녹음