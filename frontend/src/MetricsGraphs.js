import React, { useEffect, useRef, useState } from 'react';
import { Chart, registerables } from 'chart.js';

const MetricsGraphs = ({ selectedArea, selectedSubarea, selectedYear }) => {
  const chartRef = useRef(null);
  let chartInstance = null; // Store chart instance
  const [chartData, setChartData] = useState(null); // State to hold API data

  useEffect(() => {
    Chart.register(...registerables); // Register all components, including scales

    // Fetch data from the API whenever selectedArea, selectedSubarea, or selectedYear changes
    const fetchMetricsData = async () => {
      try {
        const response = await fetch(`/api/metrics-data?area_id=${selectedArea}&subarea_id=${selectedSubarea}&year=${selectedYear}`);
        const data = await response.json();

        // Transform the data to fit into chart format
        const labels = data.map(item => `Interval ${item.interval_id}`);
        const datasetData = data.map(item => item.record_count);

        setChartData({
          labels: labels,
          datasets: [{
            label: 'Records by Interval',
            data: datasetData,
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1
          }]
        });
      } catch (error) {
        console.error('Error fetching metrics data:', error);
      }
    };

    fetchMetricsData();

  }, [selectedArea, selectedSubarea, selectedYear]); // Rerun effect when these props change

  useEffect(() => {
    if (chartRef.current && chartData) {
      const ctx = chartRef.current.getContext('2d');

      // Destroy the previous chart instance if it exists
      if (chartInstance) {
        chartInstance.destroy();
      }

      chartInstance = new Chart(ctx, {
        type: 'bar',
        data: chartData,  // Use the chartData state
        options: {
          scales: {
            y: {
              beginAtZero: true,
            },
          },
        },
      });
    }

    // Cleanup function to destroy the chart instance when the component unmounts or updates
    return () => {
      if (chartInstance) {
        chartInstance.destroy();
      }
    };
  }, [chartData]);  // Re-run when chartData changes

  return (
    <div>
      <h3>Metrics Chart</h3>
      <canvas ref={chartRef}></canvas>
    </div>
  );
};

export default MetricsGraphs;
