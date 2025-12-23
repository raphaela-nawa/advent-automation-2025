'use client';

// Section 2 - Performance Trends Component
// Displays revenue trend over time using Chart.js

import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip
);

export default function PerformanceTrends({ revenueData }) {
  if (!revenueData || revenueData.length === 0) {
    return (
      <section className="performance-trends">
        <h2>Revenue Trend</h2>
        <p>No revenue data available</p>
      </section>
    );
  }

  const chartData = {
    labels: revenueData.map(d => {
      const date = new Date(d.date);
      return `${date.getMonth() + 1}/${date.getDate()}`;
    }),
    datasets: [{
      label: 'Revenue ($)',
      data: revenueData.map(d => d.revenue),
      borderColor: '#333',
      backgroundColor: 'transparent',
      tension: 0.1
    }]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: { display: false },
      tooltip: {
        callbacks: {
          label: function(context) {
            return `Revenue: $${context.parsed.y.toFixed(2)}`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value) {
            return '$' + value;
          }
        }
      }
    }
  };

  return (
    <section className="performance-trends">
      <h2>Revenue Trend (Last 90 Days)</h2>
      <div style={{ height: '300px' }}>
        <Line data={chartData} options={options} />
      </div>
    </section>
  );
}
