# Audio Comparison App

![Screenshot of the main audio comparison UI.](https://hosting.photobucket.com/bbcfb0d4-be20-44a0-94dc-65bff8947cf2/d1dadd2e-ed8d-4af7-b6d8-882d28ec4b90.png)

This project compares two audio files using digital signal processing techniques. It provides detailed visual comparisons of audio features like tempo, loudness, spectral characteristics and rhythm via interactive D3 bar charts.

## Getting Started

### 1. Clone the Repo

```bash
git clone git@github.com:devbret/audio-comparison-app.git
cd audio-comparison-app
```

### 2. Start the Backend (Flask)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

By default, the backend runs on `http://127.0.0.1:5000`.

### 3. Start the Frontend (React)

```bash
cd ../frontend
npm install
npm run dev
```

This starts the app at `http://localhost:5173` and proxies API calls to the backend.
