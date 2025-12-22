"""
Day 19 - Maritime Underwater Noise Mapping
Interactive Map Visualization using Folium

This script creates an interactive HTML map showing:
1. Noise intensity grid (choropleth heatmap)
2. Vessel position markers (color-coded by type)
3. Interactive tooltips and layer controls

Decision Support: Helps marine spatial planners identify which 3 areas need
noise mitigation measures this quarter based on noise intensity and vessel traffic.
"""

import pandas as pd
import folium
from folium.plugins import HeatMap
import branca.colormap as cm
from pathlib import Path
import json

# CRITICAL: All paths use LOCAL day19 directory structure
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / 'data'
PROCESSED_DIR = DATA_DIR / 'processed'

# ============================================================================
# Configuration
# ============================================================================

# Gulf of Mexico map center
DAY19_MAP_CENTER = [28.5, -91.5]
DAY19_MAP_ZOOM = 7

# Vessel type color mapping
DAY19_VESSEL_COLORS = {
    'Cargo': '#3388ff',      # Blue
    'Tanker': '#ff3333',     # Red
    'Passenger': '#33ff33',  # Green
    'Fishing': '#ff9933',    # Orange
    'Other': '#999999'       # Gray
}

# Noise threshold for hotspot identification
DAY19_NOISE_THRESHOLD_HIGH = 170.0  # dB - high impact
DAY19_NOISE_THRESHOLD_MEDIUM = 165.0  # dB - moderate impact


# ============================================================================
# Data Loading
# ============================================================================

def day19_load_processed_data():
    """Load processed data from day19/data/processed/ directory."""

    print(f"\n📂 Loading processed data from {PROCESSED_DIR}...")

    # Load grid data
    grid_file = PROCESSED_DIR / 'grid_noise_gulf_of_mexico.csv'
    if not grid_file.exists():
        raise FileNotFoundError(
            f"Grid data not found: {grid_file}\n"
            f"Run day19_data_prep.py first to generate processed data."
        )

    df_grid = pd.read_csv(grid_file)
    print(f"   ✅ Loaded grid data: {len(df_grid):,} cells")

    # Load vessel sample
    vessel_file = PROCESSED_DIR / 'vessel_positions_sample.csv'
    if not vessel_file.exists():
        raise FileNotFoundError(
            f"Vessel data not found: {vessel_file}\n"
            f"Run day19_data_prep.py first to generate processed data."
        )

    df_vessels = pd.read_csv(vessel_file)
    print(f"   ✅ Loaded vessel sample: {len(df_vessels):,} positions")

    return df_grid, df_vessels


# ============================================================================
# Map Creation Functions
# ============================================================================

def day19_create_base_map(center=DAY19_MAP_CENTER, zoom=DAY19_MAP_ZOOM):
    """Create base Folium map."""

    print(f"\n🗺️ Creating base map (center: {center}, zoom: {zoom})...")

    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles='CartoDB positron',
        attr='Day 19 - Maritime Noise Analysis | Gulf of Mexico'
    )

    print("   ✅ Base map created")
    return m


def day19_add_noise_grid_layer(m, df_grid):
    """Add noise intensity grid as choropleth layer."""

    print("\n📊 Adding noise intensity grid layer...")

    # Filter to cells with data
    grid_active = df_grid[df_grid['vessel_count'] > 0].copy()

    if len(grid_active) == 0:
        print("   ⚠️ No active grid cells to display")
        return m

    # Create color scale
    noise_min = grid_active['noise_mean'].min()
    noise_max = grid_active['noise_mean'].max()

    colormap = cm.LinearColormap(
        colors=['#90EE90', '#FFFF00', '#FFA500', '#FF4500', '#8B0000'],
        vmin=noise_min,
        vmax=noise_max,
        caption='125 Hz Noise Level (dB re 1 µPa @ 1m)'
    )

    # Create feature group for grid
    grid_layer = folium.FeatureGroup(name='Noise Intensity Grid (2.5km cells)', show=True)

    # Add rectangles for each grid cell
    for idx, row in grid_active.iterrows():
        # Calculate cell bounds
        bounds = [
            [row['grid_lat'], row['grid_lon']],
            [row['grid_lat'] + 0.025, row['grid_lon'] + 0.025]
        ]

        # Determine impact level
        if row['noise_mean'] >= DAY19_NOISE_THRESHOLD_HIGH:
            impact = "HIGH IMPACT"
        elif row['noise_mean'] >= DAY19_NOISE_THRESHOLD_MEDIUM:
            impact = "MODERATE IMPACT"
        else:
            impact = "Low impact"

        # Create tooltip
        tooltip_html = f"""
        <div style="font-family: Arial; font-size: 12px;">
            <b>Grid Cell Noise Analysis</b><br>
            <hr style="margin: 5px 0;">
            <b>Noise Level:</b> {row['noise_mean']:.1f} dB<br>
            <b>Impact:</b> {impact}<br>
            <b>Vessel Count:</b> {int(row['vessel_count'])}<br>
            <b>Dominant Type:</b> {row['dominant_vessel_type']}<br>
            <hr style="margin: 5px 0;">
            <small>Range: {row['noise_min']:.1f} - {row['noise_max']:.1f} dB</small>
        </div>
        """

        # Add rectangle
        folium.Rectangle(
            bounds=bounds,
            color='gray',
            weight=0.5,
            fill=True,
            fillColor=colormap(row['noise_mean']),
            fillOpacity=0.6,
            tooltip=folium.Tooltip(tooltip_html, sticky=False)
        ).add_to(grid_layer)

    grid_layer.add_to(m)
    colormap.add_to(m)

    print(f"   ✅ Added {len(grid_active):,} grid cells")
    return m


def day19_add_vessel_markers_layer(m, df_vessels):
    """Add vessel position markers."""

    print("\n🚢 Adding vessel position markers...")

    # Create feature group
    vessel_layer = folium.FeatureGroup(name='Vessel Positions (Sample: 500)', show=True)

    # Add markers
    for idx, row in df_vessels.iterrows():
        color = DAY19_VESSEL_COLORS.get(row['vessel_class'], '#999999')

        # Create popup
        popup_html = f"""
        <div style="font-family: Arial; font-size: 11px; width: 200px;">
            <b>Vessel Information</b><br>
            <hr style="margin: 5px 0;">
            <b>MMSI:</b> {int(row['MMSI'])}<br>
            <b>Type:</b> {row['vessel_class']}<br>
            <b>Speed:</b> {row['SOG']:.1f} knots<br>
            <b>Length:</b> {row['Length']:.0f} m<br>
            <b>Noise Emission:</b> {row['emission_125hz_dB']:.1f} dB<br>
            <hr style="margin: 5px 0;">
            <small>Position: {row['LAT']:.4f}°, {row['LON']:.4f}°</small>
        </div>
        """

        folium.CircleMarker(
            location=[row['LAT'], row['LON']],
            radius=4,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{row['vessel_class']} vessel"
        ).add_to(vessel_layer)

    vessel_layer.add_to(m)

    print(f"   ✅ Added {len(df_vessels):,} vessel markers")
    return m


def day19_add_legend(m):
    """Add custom legend for vessel types."""

    print("\n📋 Adding vessel type legend...")

    legend_html = '''
    <div style="position: fixed;
                bottom: 50px; right: 50px;
                background-color: white;
                border: 2px solid grey;
                border-radius: 5px;
                padding: 10px;
                font-size: 12px;
                z-index: 9999;">
        <p style="margin: 0 0 5px 0; font-weight: bold;">Vessel Types</p>
        <p style="margin: 2px 0;"><span style="color: #3388ff;">●</span> Cargo</p>
        <p style="margin: 2px 0;"><span style="color: #ff3333;">●</span> Tanker</p>
        <p style="margin: 2px 0;"><span style="color: #33ff33;">●</span> Passenger</p>
        <p style="margin: 2px 0;"><span style="color: #ff9933;">●</span> Fishing</p>
        <p style="margin: 2px 0;"><span style="color: #999999;">●</span> Other</p>
    </div>
    '''

    m.get_root().html.add_child(folium.Element(legend_html))

    print("   ✅ Legend added")
    return m


def day19_identify_hotspots(df_grid, top_n=3):
    """Identify top noise hotspot areas for decision support."""

    print(f"\n🎯 Identifying top {top_n} noise hotspot areas...")

    # Filter active cells and sort by noise
    hotspots = df_grid[df_grid['vessel_count'] > 0].nlargest(top_n, 'noise_mean')

    print("\n" + "=" * 70)
    print("🚨 TOP NOISE HOTSPOTS REQUIRING MITIGATION")
    print("=" * 70)

    for idx, (i, row) in enumerate(hotspots.iterrows(), 1):
        print(f"\n{idx}. PRIORITY AREA {idx}")
        print(f"   Location: {row['center_lat']:.3f}°N, {row['center_lon']:.3f}°W")
        print(f"   Noise Level: {row['noise_mean']:.1f} dB (avg), Peak: {row['noise_max']:.1f} dB")
        print(f"   Vessel Traffic: {int(row['vessel_count'])} vessels")
        print(f"   Dominant Type: {row['dominant_vessel_type']}")

        # Recommendation
        if row['noise_mean'] >= DAY19_NOISE_THRESHOLD_HIGH:
            print(f"   ⚠️ RECOMMENDATION: Immediate intervention (speed restrictions, route adjustment)")
        elif row['noise_mean'] >= DAY19_NOISE_THRESHOLD_MEDIUM:
            print(f"   ⚠️ RECOMMENDATION: Monitor closely, consider seasonal restrictions")

    print("\n" + "=" * 70)

    return hotspots


# ============================================================================
# Main Execution
# ============================================================================

def day19_create_maritime_noise_map():
    """Main function to create complete maritime noise map."""

    print("\n" + "=" * 70)
    print("DAY 19 - MARITIME NOISE INTERACTIVE MAP GENERATION")
    print("=" * 70)

    try:
        # Load data
        df_grid, df_vessels = day19_load_processed_data()

        # Create base map
        m = day19_create_base_map()

        # Add layers
        m = day19_add_noise_grid_layer(m, df_grid)
        m = day19_add_vessel_markers_layer(m, df_vessels)
        m = day19_add_legend(m)

        # Add layer control
        folium.LayerControl(position='topright', collapsed=False).add_to(m)

        # Identify hotspots for decision support
        hotspots = day19_identify_hotspots(df_grid, top_n=3)

        # Save map
        output_file = PROJECT_ROOT / 'day19_maritime_noise_map.html'
        m.save(str(output_file))

        print("\n" + "=" * 70)
        print("✅ INTERACTIVE MAP CREATED SUCCESSFULLY!")
        print("=" * 70)
        print(f"\n📂 Output: {output_file}")
        print(f"   File size: {output_file.stat().st_size / 1024:.1f} KB")
        print(f"\n🌐 Open in browser: file://{output_file}")
        print("\n🎯 Map Features:")
        print(f"   • Noise intensity grid: {len(df_grid[df_grid['vessel_count'] > 0]):,} active cells")
        print(f"   • Vessel markers: {len(df_vessels):,} positions")
        print(f"   • Interactive tooltips: Click cells/vessels for details")
        print(f"   • Layer control: Toggle noise grid and vessel layers")

        return output_file, hotspots

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise


if __name__ == '__main__':
    output_file, hotspots = day19_create_maritime_noise_map()
