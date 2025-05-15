import React, { useEffect } from "react";
import * as d3 from "d3";

interface AudioFeatureData {
  file1Name: string;
  file2Name: string;
  // now strictly numeric entries
  features1: Record<string, number>;
  features2: Record<string, number>;
}

interface Props {
  data: AudioFeatureData;
}

const ResultsVisualization: React.FC<Props> = ({ data }) => {
  useEffect(() => {
    // Expanded to include the remaining scalar features
    const featureKeys = [
      "sampling_rate_hz",
      "duration_s",
      "beat_count",
      "estimated_tempo_bpm",
      "loudness_rms_mean",
      "harmonic_energy",
      "percussive_energy",
      "spectral_centroid_mean",
      "spectral_bandwidth_mean",
      "spectral_rolloff_mean",
      "zero_crossing_rate_mean",
      "spectral_flux_mean",
    ];

    // clear existing svgs
    d3.selectAll(".feature-chart svg").remove();

    featureKeys.forEach((key) => {
      const val1 = data.features1?.[key];
      const val2 = data.features2?.[key];
      const chartData = [
        {
          name: data.file1Name,
          value: typeof val1 === "number" && isFinite(val1) ? val1 : 0,
        },
        {
          name: data.file2Name,
          value: typeof val2 === "number" && isFinite(val2) ? val2 : 0,
        },
      ];

      const margin = { top: 20, right: 30, bottom: 40, left: 60 },
        width = 400 - margin.left - margin.right,
        height = 150 - margin.top - margin.bottom;

      const svg = d3
        .select(`#${key}`)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

      const x = d3
        .scaleBand()
        .range([0, width])
        .domain(chartData.map((d) => d.name))
        .padding(0.4);

      svg
        .append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x));

      const y = d3
        .scaleLinear()
        .domain([0, d3.max(chartData, (d) => d.value)! * 1.1])
        .range([height, 0]);

      svg.append("g").call(d3.axisLeft(y));

      svg
        .selectAll("bars")
        .data(chartData)
        .enter()
        .append("rect")
        .attr("x", (d) => x(d.name)!)
        .attr("y", (d) => y(d.value))
        .attr("width", x.bandwidth())
        .attr("height", (d) => height - y(d.value))
        .attr("fill", (_d, i) => (i === 0 ? "#69b3a2" : "#404080"));

      svg
        .selectAll("text.label")
        .data(chartData)
        .enter()
        .append("text")
        .attr("class", "label")
        .attr("x", (d) => x(d.name)! + x.bandwidth() / 2)
        .attr("y", (d) => y(d.value) - 5)
        .attr("text-anchor", "middle")
        .style("font-size", "10px")
        .text((d) => d.value.toFixed(2));
    });
  }, [data]);

  return (
    <div className="d3-visualization">
      <h3>Audio Feature Comparison</h3>
      <div className="feature-grid">
        {[
          "sampling_rate_hz",
          "duration_s",
          "beat_count",
          "estimated_tempo_bpm",
          "loudness_rms_mean",
          "harmonic_energy",
          "percussive_energy",
          "spectral_centroid_mean",
          "spectral_bandwidth_mean",
          "spectral_rolloff_mean",
          "zero_crossing_rate_mean",
          "spectral_flux_mean",
        ].map((featureKey) => (
          <div key={featureKey} id={featureKey} className="feature-chart">
            <h4 style={{ textTransform: "capitalize" }}>
              {featureKey.replace(/_/g, " ")}
            </h4>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ResultsVisualization;
