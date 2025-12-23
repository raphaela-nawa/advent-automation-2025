// Section 3 - Listings Summary Component
// Displays property cards with key metrics, clickable to view details

export default function ListingsSummary({ properties, onSelectProperty }) {
  if (!properties || properties.length === 0) {
    return (
      <section className="listings-summary">
        <h2>Properties</h2>
        <p>No properties available</p>
      </section>
    );
  }

  return (
    <section className="listings-summary">
      <h2>Properties</h2>
      <div className="property-grid">
        {properties.map(property => (
          <div
            key={property.property_id}
            className="property-card"
            onClick={() => onSelectProperty(property.property_id)}
            style={{ cursor: 'pointer' }}
            title="Click to view details"
          >
            <div className="property-header">
              <div className="property-id">{property.property_id}</div>
              <div className="property-name">{property.property_name}</div>
            </div>
            <div className="property-metrics">
              <div className="property-metric">
                <span className="metric-label">Occupancy:</span>
                <span className="metric-value">{property.occupancy_rate}%</span>
              </div>
              <div className="property-metric">
                <span className="metric-label">Revenue:</span>
                <span className="metric-value">${property.total_revenue.toLocaleString()}</span>
              </div>
              <div className="property-metric">
                <span className="metric-label">Avg Price:</span>
                <span className="metric-value">${property.average_price.toFixed(2)}</span>
              </div>
            </div>
            <div className="view-details">→ View Details</div>
          </div>
        ))}
      </div>
    </section>
  );
}
