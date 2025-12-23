// Section 4 - Listing Detail Component
// Property drill-down view with bookings and platform stats

export default function ListingDetail({ property, onBack }) {
  if (!property) return null;

  const {
    property_id,
    property_name,
    occupancy_rate,
    total_revenue,
    average_price,
    bookings = [],
    platform_stats = {}
  } = property;

  return (
    <section className="listing-detail">
      <button onClick={onBack} className="back-button">
        ← Back to Properties
      </button>

      <div className="detail-header">
        <h2>{property_id}</h2>
        <p className="property-subtitle">{property_name}</p>
      </div>

      <div className="detail-kpis">
        <div className="detail-kpi-card">
          <div className="kpi-value">{occupancy_rate}%</div>
          <div className="kpi-label">Occupancy</div>
        </div>
        <div className="detail-kpi-card">
          <div className="kpi-value">${total_revenue.toLocaleString()}</div>
          <div className="kpi-label">Total Revenue</div>
        </div>
        <div className="detail-kpi-card">
          <div className="kpi-value">${average_price.toFixed(2)}</div>
          <div className="kpi-label">Avg Price</div>
        </div>
      </div>

      {/* Platform Statistics */}
      {Object.keys(platform_stats).length > 0 && (
        <div className="platform-stats-section">
          <h3>Platform Performance</h3>
          <div className="platform-stats-grid">
            {Object.entries(platform_stats).map(([platform, stats]) => (
              <div key={platform} className="platform-stat-card">
                <div className="platform-name">{platform.replace('_', ' ').toUpperCase()}</div>
                <div className="platform-metrics">
                  <div>Bookings: {stats.bookings}</div>
                  <div>Revenue: ${stats.revenue.toLocaleString()}</div>
                  <div>Avg Price: ${stats.avg_price.toFixed(2)}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Bookings */}
      {bookings && bookings.length > 0 && (
        <div className="bookings-section">
          <h3>Recent Bookings</h3>
          <div className="bookings-table-container">
            <table className="bookings-table">
              <thead>
                <tr>
                  <th>Booking ID</th>
                  <th>Platform</th>
                  <th>Check-in</th>
                  <th>Guests</th>
                  <th>Price</th>
                </tr>
              </thead>
              <tbody>
                {bookings.slice(0, 10).map((booking, idx) => (
                  <tr key={idx}>
                    <td>{booking.booking_id}</td>
                    <td className="platform-badge">{booking.platform}</td>
                    <td>{new Date(booking.check_in).toLocaleDateString()}</td>
                    <td>{booking.guest_count}</td>
                    <td>${booking.total_price.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </section>
  );
}
