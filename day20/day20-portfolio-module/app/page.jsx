'use client';

// Main Portfolio Module Page
// Integrates all 4 sections with state management and navigation

import { useState, useEffect } from 'react';
import HostOverview from '../components/HostOverview';
import PerformanceTrends from '../components/PerformanceTrends';
import ListingsSummary from '../components/ListingsSummary';
import ListingDetail from '../components/ListingDetail';

export default function PortfolioModule() {
  const [data, setData] = useState(null);
  const [selectedProperty, setSelectedProperty] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/data/portfolio_data.json')
      .then(res => {
        if (!res.ok) throw new Error('Failed to load data');
        return res.json();
      })
      .then(jsonData => {
        setData(jsonData);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="portfolio-module">
        <div className="loading">Loading portfolio data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="portfolio-module">
        <div className="error">Error: {error}</div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="portfolio-module">
        <div className="error">No data available</div>
      </div>
    );
  }

  // Find selected property details
  const currentProperty = selectedProperty
    ? data.properties.find(p => p.property_id === selectedProperty)
    : null;

  return (
    <div className="portfolio-module">
      {!selectedProperty ? (
        <>
          <HostOverview data={data.portfolio_overview} />
          <PerformanceTrends revenueData={data.revenue_by_day} />
          <ListingsSummary
            properties={data.properties}
            onSelectProperty={setSelectedProperty}
          />
        </>
      ) : (
        <ListingDetail
          property={currentProperty}
          onBack={() => setSelectedProperty(null)}
        />
      )}
    </div>
  );
}
