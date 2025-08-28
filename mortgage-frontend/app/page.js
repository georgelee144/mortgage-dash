"use client";

import { useState, useEffect } from "react";
import Plot from "react-plotly.js";

export default function Home() {
  const [activeTab, setActiveTab] = useState("calculator");
  const [loanAmount, setLoanAmount] = useState(500000);
  const [propertyValue, setPropertyValue] = useState(600000);
    const [annualRate, setAnnualRate] = useState('');
  const [termInMonths, setTermInMonths] = useState(360);

}
