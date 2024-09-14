import sounddevice as sd
from scipy.io.wavfile import write

duration = 5

print("Start recording...")
sr = 22050
audio_data = sd.rec(int(duration * sr), samplerate=sr, channels=1)
sd.wait()
print("Recording stopped!")
write("output.wav", sr, audio_data)
