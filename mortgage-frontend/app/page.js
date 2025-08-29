"use client";

import { useState, useEffect } from "react";
import Plot from "react-plotly.js";

export default function Home() {
  // --- State Management ---
  const [activeTab, setActiveTab] = useState("calculator");

  // Input states
  const [loanAmount, setLoanAmount] = useState(500000);
  const [propertyValue, setPropertyValue] = useState(600000);
  const [annualRate, setAnnualRate] = useState("");
  const [termInMonths, setTermInMonths] = useState(360);
  const [priceIndexKey, setPriceIndexKey] = useState(
    "S&P CoreLogic Case-Shiller U.S. National Home Price Index"
  );

  // Data states
  const [amortizationData, setAmortizationData] = useState([]);
  const [monteCarloData, setMonteCarloData] = useState(null);

  const [isAmortizationLoading, setIsAmortizationLoading] = useState(false);
  const [isMonteCarloLoading, setIsMonteCarloLoading] = useState(false);
  const [error, setError] = useState("");

  const API_BASE_URL = "http://127.0.0.1:5000";

  //--- Data Fetching ---
  // Fetch the initial interest rate when the component first loads.
  useEffect(() => {
    const fetchInitalRate = async () => {
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
    fetchInitalRate();
  }, []); //This is set to only run once on mount

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

  //Handler for the Monte Carlo Simulation
  const handleRunSimulation = async () => {
    
  };
}
