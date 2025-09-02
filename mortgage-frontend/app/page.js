"use client"; // This directive is required for using React hooks.

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";

// --- Dynamically import the Plot component with SSR turned off ---
const Plot = dynamic(() => import("react-plotly.js"), {
  ssr: false,
});

// --- Main Component ---
export default function Home() {
  // --- State Management ---
  const [activeTab, setActiveTab] = useState("calculator");
  const [graphType, setGraphType] = useState("area");

  // Input states
  const [loanAmount, setLoanAmount] = useState();
  const [propertyValue, setPropertyValue] = useState();
  const [annualRate, setAnnualRate] = useState(0);
  const [termInMonths, setTermInMonths] = useState(360);
  const [priceIndexKey, setPriceIndexKey] = useState(
    "S&P CoreLogic Case-Shiller U.S. National Home Price Index"
  );

  // Data states
  const [amortizationData, setAmortizationData] = useState([]);
  const [monteCarloData, setMonteCarloData] = useState(null);

  // UI states
  const [isAmortizationLoading, setIsAmortizationLoading] = useState(false);
  const [isMonteCarloLoading, setIsMonteCarloLoading] = useState(false);
  const [error, setError] = useState("");

  const API_BASE_URL = "http://127.0.0.1:5000";

  // --- Data Fetching ---

  // Fetch the initial interest rate when the component first loads.
  useEffect(() => {
    const fetchInitialRate = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/current-rate`);
        if (!response.ok) throw new Error("Network response was not ok");
        const data = await response.json();
        if (data.rate) {
          setAnnualRate(data.rate.toFixed(2));
        }
      } catch (err) {
        console.error("Failed to fetch current rate:", err);
        setError("Could not fetch the current interest rate from the server.");
      }
    };
    fetchInitialRate();
  }, []); // Empty dependency array means this runs only once on mount.

  // Handler for the Amortization Calculator
  const handleCalculateAmortization = async () => {
    setIsAmortizationLoading(true);
    setAmortizationData([]);
    setError("");
    try {
      const response = await fetch(`${API_BASE_URL}/api/amortization`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          loanAmount,
          propertyValue,
          annualRate,
          termInMonths,
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Calculation failed");
      setAmortizationData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsAmortizationLoading(false);
    }
  };

  // Handler for the Monte Carlo Simulation
  const handleRunSimulation = async () => {
    setIsMonteCarloLoading(true);
    setMonteCarloData(null);
    setError("");
    try {
      const response = await fetch(`${API_BASE_URL}/api/monte-carlo`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ propertyValue, termInMonths, priceIndexKey }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Simulation failed");
      setMonteCarloData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsMonteCarloLoading(false);
    }
  };
  //Handler to download the amortization table as a CSV file.
  const handleDownloadCSV = () => {
    if (amortizationData.length === 0) return;

    const headers = Object.keys(amortizationData[0]);
    const csvContent = [
      headers.join(","),
      ...amortizationData.map((row) =>
        headers.map((header) => row[header]).join(",")
      ),
    ].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    if (link.href) {
      URL.revokeObjectURL(link.href);
    }
    const url = URL.createObjectURL(blob);
    link.href = url;
    link.setAttribute("download", "amortization_schedule.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getAmortizationPlotData = () => {
    const baseLayout = {
      title: "Equity vs. Debt Over Time",
      yaxis: { title: "Amount ($)" },
      xaxis: { title: "Month" },
      legend: { x: 0.01, y: 0.98 },
    };

    switch (graphType) {
      case "bar":
        return {
          data: [
            {
              name: "Equity",
              x: amortizationData.map((d) => d.period),
              y: amortizationData.map((d) => d.equity),
              type: "bar",
              marker: { color: "#68d391" },
            },
            {
              name: "Remaining Debt",
              x: amortizationData.map((d) => d.period),
              y: amortizationData.map((d) => d.ending_principal),
              type: "bar",
              marker: { color: "#fc8181" },
            },
          ],
          layout: { ...baseLayout, barmode: "stack" },
        };
      case "line":
        return {
          data: [
            {
              name: "Equity",
              x: amortizationData.map((d) => d.period),
              y: amortizationData.map((d) => d.equity),
              type: "scatter",
              mode: "lines",
              line: { color: "#68d391" },
            },
            {
              name: "Remaining Debt",
              x: amortizationData.map((d) => d.period),
              y: amortizationData.map((d) => d.ending_principal),
              type: "scatter",
              mode: "lines",
              line: { color: "#fc8181" },
            },
          ],
          layout: baseLayout,
        };
      case "area":
        return {
          data: [
            {
              name: "Equity",
              x: amortizationData.map((d) => d.period),
              y: amortizationData.map((d) => d.equity),
              type: "scatter",
              mode: "lines",
              fill: "tozeroy",
              stackgroup: "one",
              line: { color: "#68d391" },
            },
            {
              name: "Remaining Debt",
              x: amortizationData.map((d) => d.period),
              y: amortizationData.map((d) => d.ending_principal),
              type: "scatter",
              mode: "lines",
              fill: "tozeroy",
              stackgroup: "one",
              line: { color: "#fc8181" },
            },
          ],
          layout: baseLayout,
        };
      default:
        return { data: [], layout: baseLayout };
    }
  };
  //---Rendering Logic---
  return (
    <main className="container">
      <h1 className="header">Home Buyer's Financial Dashboard</h1>

      {/* Tab Navigation */}
      <div className="tabs">
        <div
          className={`tab ${activeTab === "calculator" ? "active" : ""}`}
          onClick={() => setActiveTab("calculator")}
        >
          Mortgage Calculator
        </div>
        <div
          className={`tab ${activeTab === "simulation" ? "active" : ""}`}
          onClick={() => setActiveTab("simulation")}
        >
          Property Value Simulation
        </div>
      </div>

      {/* Input Form */}
      <div className="inputGrid">
        <div className="inputGroup">
          <label className="label" htmlFor="loanAmount">
            Loan Amount ($)
          </label>
          <input
            id="loanAmount"
            className="input"
            type="number"
            value={loanAmount}
            onChange={(e) => setLoanAmount(Number(e.target.value))}
          />
        </div>
        <div className="inputGroup">
          <label className="label" htmlFor="propertyValue">
            Property Value ($)
          </label>
          <input
            id="propertyValue"
            className="input"
            type="number"
            value={propertyValue}
            onChange={(e) => setPropertyValue(Number(e.target.value))}
          />
        </div>
        <div className="inputGroup">
          <label className="label" htmlFor="annualRate">
            Annual Interest Rate (%)
          </label>
          <input
            id="annualRate"
            className="input"
            type="number"
            value={annualRate}
            onChange={(e) => setAnnualRate(e.target.value)}
          />
        </div>
        <div className="inputGroup">
          <label className="label" htmlFor="termInMonths">
            Loan Term (Months)
          </label>
          <input
            id="termInMonths"
            className="input"
            type="number"
            value={termInMonths}
            onChange={(e) => setTermInMonths(Number(e.target.value))}
          />
        </div>
        {/*---Dropdown menu to select the graph type---*/}
        {activeTab === "calculator" && (
          <div className="inputGroup">
            <label className="label" htmlFor="graphType">
              Graph Type
            </label>
            <select
              id="graphType"
              className="select"
              value={graphType}
              onChange={(e) => setGraphType(e.target.value)}
            >
              <option value="bar">Bar Graph</option>
              <option value="line">Line Graph</option>
            </select>
          </div>
        )}
        {activeTab === "simulation" && (
          <div className="inputGroup">
            <label className="label" htmlFor="priceIndex">
              Price Index for Simulation
            </label>
            <select
              id="priceIndex"
              className="select"
              value={priceIndexKey}
              onChange={(e) => setPriceIndexKey(e.target.value)}
            >
              <option>
                S&P CoreLogic Case-Shiller U.S. National Home Price Index
              </option>
            </select>
          </div>
        )}
        {activeTab === "calculator" ? (
          <button
            className="button"
            onClick={handleCalculateAmortization}
            disabled={isAmortizationLoading}
          >
            {isAmortizationLoading ? (
              <div className="spinner"></div>
            ) : (
              "Calculate Amortization"
            )}
          </button>
        ) : (
          <button
            className="button"
            onClick={handleRunSimulation}
            disabled={isMonteCarloLoading}
          >
            {isMonteCarloLoading ? (
              <div className="spinner"></div>
            ) : (
              "Run Simulation"
            )}
          </button>
        )}
      </div>

      {error && <div className="error">{error}</div>}

      {/* Conditional Rendering for Plots */}
      <div className="plotContainer">
        {activeTab === "calculator" && amortizationData.length > 0 && (
          <Plot
            data={[
              {
                name: "Equity",
                x: amortizationData.map((d) => d.period),
                y: amortizationData.map((d) => d.equity),
                type: "scatter",
                mode: "lines",
                stackgroup: "one",
                marker: { color: "#68d391" },
              },
              {
                name: "Remaining Debt",
                x: amortizationData.map((d) => d.period),
                y: amortizationData.map((d) => d.ending_principal),
                type: "scatter",
                mode: "lines",
                stackgroup: "one",
                marker: { color: "#fc8181" },
              },
            ]}
            layout={{
              title: "Equity vs. Debt Over Time",
              yaxis: { title: "Amount ($)" },
              xaxis: { title: "Month" },
            }}
            style={{ width: "100%", height: "500px" }}
            useResizeHandler
          />
        )}
        {activeTab === "simulation" && monteCarloData && (
          <Plot
            data={[
              ...Object.keys(monteCarloData.runs).map((runKey) => ({
                name: `Run ${runKey}`,
                x: monteCarloData.periods,
                y: monteCarloData.runs[runKey],
                type: "scatter",
                mode: "lines",
                line: { color: "#cbd5e0", width: 1 },
                showlegend: false,
              })),
              {
                name: "75th Percentile",
                x: monteCarloData.periods,
                y: monteCarloData.quantile_75,
                type: "scatter",
                mode: "lines",
                line: { color: "#68d391", dash: "dash" },
              },
              {
                name: "Median Projection",
                x: monteCarloData.periods,
                y: monteCarloData.median,
                type: "scatter",
                mode: "lines",
                line: { color: "#4299e1", width: 4 },
              },
              {
                name: "25th Percentile",
                x: monteCarloData.periods,
                y: monteCarloData.quantile_25,
                type: "scatter",
                mode: "lines",
                line: { color: "#fc8181", dash: "dash" },
              },
            ]}
            layout={{
              title: "Monte Carlo Property Value Simulation",
              yaxis: { title: "Projected Property Value ($)" },
              xaxis: { title: "Month" },
            }}
            style={{ width: "100%", height: "500px" }}
            useResizeHandler
          />
        )}
      </div>
      {activeTab === "calculator" && amortizationData.length > 0 && (
        <div className="tableContainer">
          <div className="tableHeader">
            <h2>Amortization Schedule</h2>
            <button className="button" onClick={handleDownloadCSV}>
              Download CSV
            </button>
          </div>
          <div className="tableWrapper">
            <table>
              <thead>
                <tr>
                  {Object.keys(amortizationData[0]).map((key) => (
                    <th key={key}>
                      {key
                        .replace(/_/g, " ")
                        .replace(/\b\w/g, (l) => l.toUpperCase())}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {amortizationData.map((row, rowIndex) => (
                  <tr key={rowIndex}>
                    {Object.keys(row).map((key, cellIndex) => {
                      const value = row[key];
                      // Conditionally format numbers. 'period' remains an integer.
                      const displayValue =
                        typeof value === "number" && key !== "period"
                          ? value.toFixed(2)
                          : value;
                      return <td key={cellIndex}>{displayValue}</td>;
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </main>
  );
}
