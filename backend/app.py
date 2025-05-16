import os
import traceback

from flask import Flask, jsonify, request
from flask_cors import CORS

import librosa
import numpy as np

application = Flask(__name__)
application.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

CORS(application, resources={r"/api/*": {"origins": [
    "http://localhost:5173", 
    "http://127.0.0.1:5173"
]}}, supports_credentials=True)

@application.route('/api/compare', methods=['POST'])
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
            # Compute STFT magnitude for spectral flux
            S = np.abs(librosa.stft(y))

            # Spectral features
            centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
            rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)

            # Zero-crossing rate
            zcr = librosa.feature.zero_crossing_rate(y=y)

            # RMS energy
            rms = librosa.feature.rms(y=y)
            rms_harm = librosa.feature.rms(y=librosa.effects.harmonic(y))
            rms_perc = librosa.feature.rms(y=librosa.effects.percussive(y))

            # Tempo and beat count
            tempo = float(librosa.beat.tempo(y=y, sr=sr)[0])
            _, beats = librosa.beat.beat_track(y=y, sr=sr)
            beat_count = len(librosa.frames_to_time(beats, sr=sr))

            # Mean spectral flux
            spectral_flux = np.sqrt(np.sum(np.diff(S, axis=1)**2, axis=0))

            return {
                "sampling_rate_hz": sr,
                "duration_s": round(librosa.get_duration(y=y, sr=sr), 2),
                "estimated_tempo_bpm": round(tempo, 2),
                "beat_count": int(beat_count),
                "loudness_rms_mean": round(float(np.mean(rms)), 6),
                "harmonic_energy": float(np.mean(rms_harm)),
                "percussive_energy": float(np.mean(rms_perc)),
                "spectral_centroid_mean": float(np.mean(centroid)),
                "spectral_bandwidth_mean": float(np.mean(bandwidth)),
                "spectral_rolloff_mean": float(np.mean(rolloff)),
                "zero_crossing_rate_mean": float(np.mean(zcr)),
                "spectral_flux_mean": float(np.mean(spectral_flux)),
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
    application.run(debug=True, port=5000)