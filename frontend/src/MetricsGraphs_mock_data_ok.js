import React, { useEffect, useRef } from 'react';
import { Chart, registerables } from 'chart.js';

const MetricsGraphs = () => {
  const chartRef = useRef(null);
  let chartInstance = null; // Store chart instance

  useEffect(() => {
    Chart.register(...registerables); // Register all components, including scales

    if (chartRef.current) {
      const ctx = chartRef.current.getContext('2d');

      // Destroy the previous chart instance if it exists
      if (chartInstance) {
        chartInstance.destroy();
      }

      chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['January', 'February', 'March', 'April', 'May'],
          datasets: [
            {
              label: 'Test Data',
              data: [12, 19, 3, 5, 2],
              backgroundColor: 'rgba(75, 192, 192, 0.2)',
              borderColor: 'rgba(75, 192, 192, 1)',
              borderWidth: 1,
            },
          ],
        },
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
  }, []); // Empty dependency array so the chart is initialized only on component mount

  return (
    <div>
      <h3>Basic Test Chart</h3>
      <canvas ref={chartRef}></canvas>
    </div>
  );
};

export default MetricsGraphs;
