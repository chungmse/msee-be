import librosa
import numpy as np
import matplotlib.pyplot as plt
import librosa.display
from scipy.signal import find_peaks

# Đọc file âm thanh
file_path = "public/music/66d6ce748a69c14d4dea137c.mp3"
y, sr = librosa.load(file_path, sr=22050)

# Tính toán spectrogram
n_fft = 2048
hop_length = 512
D = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)

# Xác định dải tần số quan tâm
fmin, fmax = 0, sr / 2  # Toàn bộ dải tần số


def create_constellation_map(spectrogram, k_max=5, percentile_threshold=99):
    constellation_map = []
    for i in range(spectrogram.shape[1]):
        time_slice = spectrogram[:, i]
        threshold = np.percentile(time_slice, percentile_threshold)
        peaks, _ = find_peaks(time_slice, height=threshold, distance=10)
        top_peaks = sorted(peaks, key=lambda x: time_slice[x], reverse=True)[:k_max]
        for peak in top_peaks:
            constellation_map.append((i, peak))
    return constellation_map


# Tạo constellation map
constellation_map = create_constellation_map(S_db)


# Hàm vẽ spectrogram
def plot_spectrogram(
    S_db,
    sr,
    hop_length,
    fmin,
    fmax,
    title,
    filename,
    constellation_map=None,
    start_time=0,
    end_time=None,
    s_dot=10,
):
    plt.figure(figsize=(20, 10))
    img = librosa.display.specshow(
        S_db,
        sr=sr,
        hop_length=hop_length,
        x_axis="time",
        y_axis="hz",
        fmin=fmin,
        fmax=fmax,
    )
    plt.colorbar(img, format="%+2.0f dB")
    plt.title(title)

    if constellation_map:
        time_coords, freq_coords = zip(*constellation_map)
        times = librosa.frames_to_time(time_coords, sr=sr, hop_length=hop_length)
        freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
        plt.scatter(
            np.array(times) - start_time,
            [freqs[min(f, len(freqs) - 1)] for f in freq_coords],
            color="red",
            s=s_dot,
            alpha=0.7,
        )

    plt.ylim(fmin, fmax)
    duration = S_db.shape[1] * hop_length / sr
    plt.xlim(0, duration)

    # Điều chỉnh trục x
    if end_time and (end_time - start_time) <= 5:  # Cho ảnh chi tiết
        x_ticks = np.linspace(0, end_time - start_time, num=5)
        plt.xticks(x_ticks, [f"{x + start_time:.1f}" for x in x_ticks])
    else:  # Cho ảnh toàn bộ
        x_ticks = np.arange(0, duration + 1, 30)  # Đánh dấu mỗi 30 giây
        plt.xticks(x_ticks, [f"{x + start_time:.0f}" for x in x_ticks])

    plt.xlabel("Time (seconds)")
    plt.grid(True, alpha=0.3)
    plt.tick_params(axis="both", which="major", labelsize=12)
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()


# Ảnh 1: Spectrogram không có điểm đánh dấu
plot_spectrogram(
    S_db, sr, hop_length, fmin, fmax, "Spectrogram (Full Song)", "spectrogram_full.png"
)

# Ảnh 2: Spectrogram với constellation map
plot_spectrogram(
    S_db,
    sr,
    hop_length,
    fmin,
    fmax,
    "Spectrogram and Constellation Map (Full Song)",
    "spectrogram_constellation_full.png",
    constellation_map,
    s_dot=2,
)

# Ảnh 3: Chi tiết từ giây 30 đến 35, từ 0Hz đến 2000Hz
start_time, end_time = 30, 35
start_frame = librosa.time_to_frames(start_time, sr=sr, hop_length=hop_length)
end_frame = librosa.time_to_frames(end_time, sr=sr, hop_length=hop_length)
freq_range = np.where(
    (librosa.fft_frequencies(sr=sr, n_fft=n_fft) >= 0)
    & (librosa.fft_frequencies(sr=sr, n_fft=n_fft) <= 2000)
)[0]

S_db_detail = S_db[freq_range[0] : freq_range[-1] + 1, start_frame:end_frame]
constellation_map_detail = [
    (t - start_frame, f - freq_range[0])
    for t, f in constellation_map
    if start_frame <= t < end_frame and freq_range[0] <= f <= freq_range[-1]
]


def plot_spectrogram_detail(
    S_db,
    sr,
    hop_length,
    fmin,
    fmax,
    title,
    filename,
    constellation_map=None,
    start_time=0,
    end_time=None,
    s_dot=10,
):
    plt.figure(figsize=(20, 10))
    img = librosa.display.specshow(
        S_db,
        sr=sr,
        hop_length=hop_length,
        x_axis="time",
        y_axis="hz",
        fmin=fmin,
        fmax=fmax,
    )
    plt.colorbar(img, format="%+2.0f dB")
    plt.title(title)

    if constellation_map:
        time_coords, freq_coords = zip(*constellation_map)
        times = librosa.frames_to_time(time_coords, sr=sr, hop_length=hop_length)
        freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)[
            freq_range[0] : freq_range[-1] + 1
        ]
        plt.scatter(
            times,
            [freqs[min(f, len(freqs) - 1)] for f in freq_coords],
            color="red",
            s=s_dot,
            alpha=0.7,
        )

    plt.ylim(fmin, fmax)
    plt.xlim(0, end_time - start_time)

    x_ticks = np.linspace(0, end_time - start_time, num=6)
    plt.xticks(x_ticks, [f"{x + start_time:.1f}" for x in x_ticks])

    plt.xlabel("Time (seconds)")
    plt.grid(True, alpha=0.3)
    plt.tick_params(axis="both", which="major", labelsize=12)
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()


plot_spectrogram_detail(
    S_db_detail,
    sr,
    hop_length,
    0,
    2000,
    "Spectrogram and Constellation Map (30-35s, 0-2000Hz)",
    "spectrogram_constellation_detail.png",
    constellation_map_detail,
    start_time,
    end_time,
)

# Thêm thông tin về đặc trưng của khu vực chi tiết
print(f"Details for the 30-35s segment:")
print(f"Number of constellation points: {len(constellation_map_detail)}")
print(f"Frequency range: 0 Hz - 2000 Hz")
print(f"Time range: {start_time}s - {end_time}s")
print(f"----------------------------------------")
print(f"Sample rate: {sr}")
print(f"Audio duration: {librosa.get_duration(y=y, sr=sr):.2f} seconds")
print(f"Shape of spectrogram: {S_db.shape}")
print(f"Frequency range: {fmin} Hz - {fmax} Hz")
print(f"Number of points in constellation map: {len(constellation_map)}")
