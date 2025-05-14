import os
import traceback

from flask import Flask, jsonify, request
from flask_cors import CORS

import librosa
import numpy as np

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

@app.route('/api/compare', methods=['POST'])
def compare_audio():
    print("Received request to /api/compare")
    if 'audio1' not in request.files or 'audio2' not in request.files:
        print("Error: Missing one or both audio files")
        return jsonify({"error": "Missing one or both audio files"}), 400

    audio_file1 = request.files['audio1']
    audio_file2 = request.files['audio2']
    filename1 = audio_file1.filename or "audio1"
    filename2 = audio_file2.filename or "audio2"

    print(f"Received files: {filename1}, {filename2}")
    try:
        print(f"Loading {filename1}...")
        y1, sr1 = librosa.load(audio_file1, sr=None)
        print(f"Loading {filename2}...")
        y2, sr2 = librosa.load(audio_file2, sr=None)
        print("Audio loaded successfully.")

        def extract_features(y, sr):
            S = np.abs(librosa.stft(y))
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            onsets_frames = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
            onsets_times = librosa.frames_to_time(onsets_frames, sr=sr)

            y_harmonic = librosa.effects.harmonic(y)
            y_percussive = librosa.effects.percussive(y)

            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
            rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
            melspec = librosa.feature.melspectrogram(y=y, sr=sr)
            tonnetz = librosa.feature.tonnetz(y=y_harmonic, sr=sr)

            rms = librosa.feature.rms(y=y)
            zcr = librosa.feature.zero_crossing_rate(y=y)
            spectral_flux = np.sqrt(np.sum(np.diff(S, axis=1)**2, axis=0))

            rms_harm = librosa.feature.rms(y=y_harmonic)
            rms_perc = librosa.feature.rms(y=y_percussive)
            harmony_energy = float(np.mean(rms_harm))
            percussive_energy = float(np.mean(rms_perc))

            return {
                "sampling_rate_hz": sr,
                "duration_s": round(librosa.get_duration(y=y, sr=sr), 2),
                "estimated_tempo_bpm": round(float(librosa.beat.tempo(y=y, sr=sr)[0]), 2),
                "beat_count": int(len(librosa.frames_to_time(librosa.beat.beat_track(y=y, sr=sr)[1], sr=sr))),
                "first_5_beat_times_s": [round(t, 2) for t in librosa.frames_to_time(librosa.beat.beat_track(y=y, sr=sr)[1], sr=sr)[:5]],
                "onsets_s": onsets_times.tolist(),
                "mfcc": mfcc.tolist(),
                "chroma": chroma.tolist(),
                "spectral_centroid": centroid[0].tolist(),
                "spectral_centroid_mean": float(np.mean(centroid)),
                "spectral_bandwidth": bandwidth[0].tolist(),
                "spectral_bandwidth_mean": float(np.mean(bandwidth)),
                "spectral_rolloff": rolloff[0].tolist(),
                "spectral_rolloff_mean": float(np.mean(rolloff)),
                "spectral_contrast": contrast.tolist(),
                "mel_spectrogram": melspec.tolist(),
                "tonnetz": tonnetz.tolist(),
                "rms": rms[0].tolist(),
                "loudness_rms_mean": round(float(np.mean(rms)), 6),
                "zero_crossing_rate": zcr[0].tolist(),
                "zero_crossing_rate_mean": float(np.mean(zcr)),
                "onset_strength": onset_env.tolist(),
                "onset_strength_mean": float(np.mean(onset_env)),
                "spectral_flux": spectral_flux.tolist(),
                "spectral_flux_mean": float(np.mean(spectral_flux)),
                "harmonic_energy": harmony_energy,
                "percussive_energy": percussive_energy
            }

        print("Extracting features for file1...")
        features1 = extract_features(y1, sr1)
        print("Extracting features for file2...")
        features2 = extract_features(y2, sr2)
        print("Feature extraction complete.")

        tempo_difference = abs(features1["estimated_tempo_bpm"] - features2["estimated_tempo_bpm"])

        results = {
            "file1": filename1,
            "file2": filename2,
            "analysis_timestamp": f"{os.times().user:.2f}s user time",
            "comparison_metrics": {
                "tempo_difference_bpm": round(tempo_difference, 2),
            },
            "features1": features1,
            "features2": features2
        }

        print("Analysis complete, sending results.")
        return jsonify(results)

    except Exception as e:
        print(f"Error during audio processing: {e}")
        print(traceback.format_exc())
        return jsonify({"error": f"An error occurred during analysis: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
