import sounddevice
from scipy.io.wavfile import write

fs = 44100  # Sample rate

seconds = 10  # Duration of recording

print("Recording...")

recorded_voice = sounddevice.rec(int(seconds * fs), samplerate=fs, channels=1)

sounddevice.wait()

print("Recording done...")

write("output.wav", fs, recorded_voice)

print("File saved as output.wav")
