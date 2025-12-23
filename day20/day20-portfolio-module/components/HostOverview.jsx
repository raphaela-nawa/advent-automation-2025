// Section 1 - Host Overview Component
// Displays portfolio-wide KPIs: occupancy, revenue, ADR, RevPAR, property count

export default function HostOverview({ data }) {
  if (!data) return null;

  const {
    occupancy_rate,
    total_revenue,
    average_daily_rate,
    revpar,
    property_count
  } = data;

  return (
    <section className="host-overview">
      <h2>Portfolio Overview</h2>
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-value">{occupancy_rate}%</div>
          <div className="kpi-label">Occupancy Rate</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-value">${total_revenue.toLocaleString()}</div>
          <div className="kpi-label">Total Revenue</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-value">${average_daily_rate.toFixed(2)}</div>
          <div className="kpi-label">Average Daily Rate</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-value">${revpar.toFixed(2)}</div>
          <div className="kpi-label">RevPAR</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-value">{property_count}</div>
          <div className="kpi-label">Properties</div>
        </div>
      </div>
    </section>
  );
}
