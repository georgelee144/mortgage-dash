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
  useEffect(()=>{
    
  })

}
