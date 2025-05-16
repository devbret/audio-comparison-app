import { useState } from "react";
import type { ChangeEvent, FormEvent } from "react";
import "./App.css";
import axios from "axios";
import ResultsVisualization from "./components/ResultsVisualization";

interface AnalysisResult {
  file1: string;
  file2: string;
  comparison_metrics: Record<string, number>;
  features1: Record<string, number>;
  features2: Record<string, number>;
}

function App() {
  // --- State Variables ---
  const [file1, setFile1] = useState<File | null>(null);
  const [file2, setFile2] = useState<File | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(
    null
  );
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // --- Event Handlers ---
  const handleFile1Change = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setFile1(event.target.files[0]);
      setAnalysisResult(null);
      setError(null);
    }
  };

  const handleFile2Change = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setFile2(event.target.files[0]);
      setAnalysisResult(null);
      setError(null);
    }
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!file1 || !file2) {
      setError("Please select both audio files before comparing.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setAnalysisResult(null);

    const formData = new FormData();
    formData.append("audio1", file1);
    formData.append("audio2", file2);

    try {
      const response = await axios.post<AnalysisResult>(
        `/api/compare`,
        formData
      );

      console.log("Received analysis data:", response.data);

      setAnalysisResult(response.data);
    } catch (err) {
      console.error("Error uploading or analyzing files:", err);
      if (axios.isAxiosError(err)) {
        if (err.response) {
          setError(
            `Analysis failed: ${
              err.response.data?.error || err.response.statusText
            } (Status: ${err.response.status})`
          );
        } else if (err.request) {
          setError(
            "Analysis failed: No response from the server. Is it running?"
          );
        } else {
          setError(`Analysis failed: ${err.message}`);
        }
      } else {
        setError(`Analysis failed: An unexpected error occurred.`);
      }
      setAnalysisResult(null);
    } finally {
      setIsLoading(false);
    }
  };

  // --- Render JSX ---
  return (
    <>
      {/* Header Section */}
      <h1>Audio Comparison App</h1>
      <p>Upload two audio files to compare them using Librosa.</p>
      {/* File Upload Form */}
      <form onSubmit={handleSubmit} className="upload-form">
        <div className="file-input-container">
          <label htmlFor="file1">Audio File 1:</label>
          <input
            type="file"
            id="file1"
            accept="audio/*"
            onChange={handleFile1Change}
            required
          />
          {file1 && (
            <span>
              Selected: {file1.name} ({(file1.size / 1024 / 1024).toFixed(2)}{" "}
              MB)
            </span>
          )}
        </div>

        <div className="file-input-container">
          <label htmlFor="file2">Audio File 2:</label>
          <input
            type="file"
            id="file2"
            accept="audio/*"
            onChange={handleFile2Change}
            required
          />
          {file2 && (
            <span>
              Selected: {file2.name} ({(file2.size / 1024 / 1024).toFixed(2)}{" "}
              MB)
            </span>
          )}
        </div>

        <button type="submit" disabled={!file1 || !file2 || isLoading}>
          {isLoading ? "Analyzing..." : "Compare Files"}
        </button>
      </form>
      {/* Display Area for Loading Indicator, Errors, and Visualization */}
      <div className="results-area">
        {/* Show loading message while analysis is in progress */}
        {isLoading && <p>Analyzing... Please wait.</p>}

        {/* Show error message if an error occurred */}
        {error && !isLoading && <p className="error-message">Error: {error}</p>}

        {/* Render the D3 Visualization Component if results are available */}
        {analysisResult && !isLoading && !error && (
          <ResultsVisualization
            data={{
              file1Name: analysisResult.file1,
              file2Name: analysisResult.file2,
              features1: analysisResult.features1,
              features2: analysisResult.features2,
            }}
          />
        )}

        {/* Initial placeholder message */}
        {!isLoading && !error && !analysisResult && (
          <p>
            Upload two audio files and click 'Compare Files' to see results.
          </p>
        )}
      </div>
    </>
  );
}

export default App;
