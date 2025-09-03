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
  const [graphType, setGraphType] = useState("area"); // 'bar', 'line', or 'area'

  // Input states
  const [loanAmount, setLoanAmount] = useState("");
  const [propertyValue, setPropertyValue] = useState("");
  const [annualRate, setAnnualRate] = useState("0");
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

  // --- Data Fetching & Handlers ---

  useEffect(() => {
    const fetchInitialRate = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/current-rate`);
        if (!response.ok) throw new Error("Network response was not ok");
        const data = await response.json();
        if (data.rate) setAnnualRate(data.rate.toFixed(2));
      } catch (err) {
        console.error("Failed to fetch current rate:", err);
        setError("Could not fetch the current interest rate from the server.");
      }
    };
    fetchInitialRate();
  }, []);

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
    switch (graphType) {
      case "bar":
        return [
          {
            name: "Equity",
            x: amortizationData.map((d) => d.period),
            y: amortizationData.map((d) => d.equity),
            type: "bar",
            marker: { color: "#4299e1" }, // Blue for Equity
          },
          {
            name: "Remaining Debt",
            x: amortizationData.map((d) => d.period),
            y: amortizationData.map((d) => d.ending_principal * -1),
            type: "bar",
            marker: { color: "#fc8181" }, // Red for Debt
          },
        ];
      case "line":
        return [
          {
            name: "Equity",
            x: amortizationData.map((d) => d.period),
            y: amortizationData.map((d) => d.equity),
            type: "scatter",
            mode: "lines",
            line: { color: "#4299e1" },
          },
          {
            name: "Remaining Debt",
            x: amortizationData.map((d) => d.period),
            y: amortizationData.map((d) => d.ending_principal),
            type: "scatter",
            mode: "lines",
            line: { color: "#fc8181" },
          },
        ];
      case "area":
        return [
          {
            name: "Equity",
            x: amortizationData.map((d) => d.period),
            y: amortizationData.map((d) => d.equity),
            type: "scatter",
            mode: "lines",
            fill: "tozeroy",
            stackgroup: "one",
            line: { color: "#4299e1" },
          },
          {
            name: "Remaining Debt",
            x: amortizationData.map((d) => d.period),
            y: amortizationData.map((d) => d.ending_principal),
            type: "scatter",
            mode: "lines",
            fill: "tonexty",
            stackgroup: "one",
            line: { color: "#fc8181" },
          },
        ];
      default:
        return [];
    }
  };

  // --- Render Logic ---
  return (
    <main className="container">
      <h1 className="header">Home Buyer's Financial Dashboard</h1>
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
        <div
          className={`tab ${activeTab === "FAQ" ? "active" : ""}`}
          onClick={() => setActiveTab("FAQ")}
        >
          Frequently Asked Questions (FAQ)
        </div>
      </div>
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
            placeholder="e.g., 500000"
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
            placeholder="e.g., 600000"
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
              <option value="area">Area Graph</option>
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
        {activeTab === "FAQ" && (
          <div>
            <h4>Mortgage Calculation</h4>
            <p>
              By default the interest rate and term in months is already
              populated. The default interest rate is the most recent average
              weekly 30 year mortgage rate from Freddie Mac, taken via FRED.
              Term in months is the number of months for 30 years, the typical
              number of years for a mortgage.
            </p>
            <p>
              Mortgage payment is calculated, by solving for the payment
              variable of the present value annuity formula.
            </p>
            {/* Insert annuity formula using latex and solve for payment */}
            {/* <p>If extra payments were added, we assumed that it was done at the end of the month.</p> */}
            <h4>Property Value Simulation</h4>
            <p>
              The property value simulation should be taken with a grain of salt
              as past performance is no guarantee of future results. It is a
              monte carlo simulation that takes the past monthly performance of
              a selected index and randomly samples monthly performance for the
              inputted loan term. There is an option to replace or not to
              replace numbers when sampling. If no indices are to your liking
              then you may upload your own monthly returns.
            </p>
            <h6>General Caution on Simulations</h6>
            <ul>
              <li>
                As stated earlier: "Past performance is no guarantee of future
                performance". However, it is widely considered to be a decent
                starting point but one should note that past performance,
                especially over long periods of time, are riddled with issues
                that make predictions hard. Data such as real estate prices can
                be considered non-stationary, statistics used to facilitate
                predictions such as the average and variance changes over time.
                This may be due to valuation paradigms, social views, and laws
                regarding real estate. The effect of those may have
                significantly influenced prices with varying intensity and over
                different time frames. Quantifying their effects is a herculean
                effort. On the other hand, interest rates is a significant
                determinant of real estate prices and have definitely changed
                over long periods.{" "}
              </li>
              <li>
                Price indices are a messy average. You should research how the
                index was constructed and whether or not they are relevant to
                your property. A broad general index may be deceptive.
                Weaknesses from declining prices in some locations and/or
                property types, may be covered up by strong sales in very
                popular locations.
              </li>
              <li>
                Price indices on illiquid assets like real estate are generally
                derived from one of two methods, either by transactions or by
                appraisals. Appraisals are subjective and should not be taken
                seriously unless transactions are not present. Ironically most
                appraisals are based on recent transactions but, based on
                personal experience, can be and usually manipulated to get a
                desired valuation. An appraisal based on transactions should
                incorporate other properties with similar features to yours. If
                there are no such transactions then a cost approach, what would
                it cost to buy and build the property, or discounted cash flow
                model, valuation based on if this was a rental property, could
                be used instead. <br></br> While transactions are preferred as
                it is what one would expect in real markets, they are still
                flawed. Real estate is a unique asset and idiosyncrasies may
                drastically change the price, an index is a dirty average of all
                that. The included properties may not be representative of your
                property in terms of property type (single family vs condo vs
                multifamily), location, local laws, neighborhood, etc.
              </li>
              <li>
                Transactions may not account for the specifics of the sale.
                Transactions are more likely to happen during favorable market
                conditions. Transactions during unfavorable market conditions
                may be overcrowded by distressed sales, like during the Great
                Financial Crisis.
              </li>
              <li>Simulation does not include any selling costs.</li>
            </ul>
          </div>
        )}
      </div>

      {error && <div className="error">{error}</div>}

      <div className="plotContainer">
        {activeTab === "calculator" && amortizationData.length > 0 && (
          <Plot
            data={getAmortizationPlotData()}
            layout={{
              title: { text: "Mortgage Amortization: Equity vs. Debt" },
              xaxis: { title: { text: "Periods (Months)" } },
              yaxis: { title: { text: "Dollars ($)" } },
              margin: { l: 60, r: 20, t: 80, b: 60 },
              legend: {
                orientation: "h",
                yanchor: "bottom",
                y: 1.02,
                xanchor: "right",
                x: 1,
              },
              hovermode: "x unified",
              barmode: graphType === "bar" ? "relative" : undefined,
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
              title: { text: "Monte Carlo Property Value Simulation" },
              yaxis: { title: { text: "Projected Property Value ($)" } },
              xaxis: { title: { text: "Month" } },
              margin: { l: 60, r: 20, t: 80, b: 60 },
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
