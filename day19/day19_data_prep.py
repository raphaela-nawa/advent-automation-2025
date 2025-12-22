"""
Day 19 - Maritime Underwater Noise Mapping
Data Preparation Script

This script processes NOAA AIS data and calculates underwater noise emissions
using the JOMOPANS-ECHO model methodology.

All data is stored locally in day19/data/ directory.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json

# CRITICAL: All paths use LOCAL day19 directory structure
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / 'data'
PROCESSED_DIR = DATA_DIR / 'processed'
RAW_DIR = DATA_DIR / 'raw'

# Ensure directories exist
PROCESSED_DIR.mkdir(exist_ok=True, parents=True)
RAW_DIR.mkdir(exist_ok=True, parents=True)

# ============================================================================
# JOMOPANS-ECHO Model Functions (copied from GIS_SymphonyLayer)
# ============================================================================

def day19_classify_vessel_from_ais(ais_type, speed_kn, length_m):
    """
    Classify vessel into JOMOPANS-ECHO categories based on AIS data.

    Args:
        ais_type: AIS vessel type code (int)
        speed_kn: Speed over ground in knots
        length_m: Vessel length in meters

    Returns:
        str: Vessel class (Cargo, Tanker, Passenger, Fishing, Other)
    """
    # AIS Type codes mapping (simplified)
    # 70-79: Cargo, 80-89: Tanker, 60-69: Passenger, 30: Fishing

    if pd.isna(ais_type) or pd.isna(length_m):
        return 'Other'

    ais_type = int(ais_type)

    # Cargo vessels
    if 70 <= ais_type <= 79:
        return 'Cargo'

    # Tankers
    if 80 <= ais_type <= 89:
        return 'Tanker'

    # Passenger vessels
    if 60 <= ais_type <= 69:
        return 'Passenger'

    # Fishing vessels
    if ais_type == 30:
        return 'Fishing'

    # Default classification by size
    if length_m > 200:
        return 'Cargo'
    elif length_m > 100:
        return 'Tanker'
    else:
        return 'Other'


def day19_calculate_125hz_emission(vessel_type, speed_kn, length_m):
    """
    Calculate 125 Hz underwater noise emission using JOMOPANS-ECHO model.

    Args:
        vessel_type: Vessel classification (Cargo, Tanker, etc.)
        speed_kn: Speed over ground in knots
        length_m: Vessel length in meters

    Returns:
        float: Source level in dB re 1 µPa @ 1m at 125 Hz
    """
    # JOMOPANS-ECHO empirical model parameters (simplified)
    # Source level = Base_Level + Speed_Factor * log(speed) + Length_Factor * log(length)

    # Default values for missing data
    if pd.isna(speed_kn) or speed_kn <= 0:
        speed_kn = 10.0  # Typical cruising speed

    if pd.isna(length_m) or length_m <= 0:
        length_m = 100.0  # Typical vessel length

    # Base source levels at 125 Hz (dB re 1 µPa @ 1m)
    base_levels = {
        'Cargo': 165.0,
        'Tanker': 168.0,
        'Passenger': 170.0,
        'Fishing': 155.0,
        'Other': 160.0
    }

    # Speed and length correction factors
    speed_factor = 20.0  # dB per decade of speed
    length_factor = 10.0  # dB per decade of length

    base_sl = base_levels.get(vessel_type, 160.0)

    # Calculate source level
    speed_correction = speed_factor * np.log10(max(speed_kn, 1.0) / 10.0)
    length_correction = length_factor * np.log10(max(length_m, 10.0) / 100.0)

    source_level = base_sl + speed_correction + length_correction

    # Clamp to realistic range (140-190 dB)
    return np.clip(source_level, 140.0, 190.0)


# ============================================================================
# Data Loading and Processing
# ============================================================================

def day19_load_ais_data(filename='AIS_2024_01_01.csv', sample_size=5000):
    """
    Load and process NOAA AIS data from local day19/data/raw/ directory.

    Args:
        filename: Name of CSV file to load
        sample_size: Number of records to sample (for 3-hour MVP constraint)

    Returns:
        pd.DataFrame: Processed AIS data with noise emissions
    """
    print(f"\n📂 Loading AIS data from day19/data/raw/{filename}")

    filepath = RAW_DIR / filename

    if not filepath.exists():
        raise FileNotFoundError(
            f"AIS data file not found: {filepath}\n"
            f"Please copy NOAA AIS data to day19/data/raw/"
        )

    # Load CSV with required columns
    required_cols = ['MMSI', 'BaseDateTime', 'LAT', 'LON', 'SOG', 'VesselType', 'Length']

    try:
        df = pd.read_csv(filepath, usecols=required_cols)
        print(f"   ✅ Loaded {len(df):,} records")
    except Exception as e:
        print(f"   ❌ Error loading file: {e}")
        raise

    # Data quality filters
    print("\n🧹 Cleaning data...")

    # Remove invalid coordinates
    df = df[(df['LAT'].between(-90, 90)) & (df['LON'].between(-180, 180))]

    # Remove invalid speeds (negative or unrealistic)
    df = df[(df['SOG'] >= 0) & (df['SOG'] <= 50)]

    # Remove records with missing critical data
    df = df.dropna(subset=['LAT', 'LON', 'MMSI'])

    print(f"   ✅ After cleaning: {len(df):,} records")

    # Geographic filter: Gulf of Mexico
    print("\n🎯 Filtering to Gulf of Mexico region...")
    DEMO_BOUNDS = {
        'min_lon': -95.0,
        'max_lon': -88.0,
        'min_lat': 27.0,
        'max_lat': 30.0
    }

    df = df[
        (df['LON'] >= DEMO_BOUNDS['min_lon']) &
        (df['LON'] <= DEMO_BOUNDS['max_lon']) &
        (df['LAT'] >= DEMO_BOUNDS['min_lat']) &
        (df['LAT'] <= DEMO_BOUNDS['max_lat'])
    ]

    print(f"   ✅ After geographic filter: {len(df):,} records")

    # Sample for MVP (3-hour constraint)
    if len(df) > sample_size:
        print(f"\n📊 Sampling {sample_size:,} records for MVP visualization...")
        df = df.sample(n=sample_size, random_state=42)

    # Classify vessels
    print("\n🚢 Classifying vessels using JOMOPANS-ECHO model...")
    df['vessel_class'] = df.apply(
        lambda row: day19_classify_vessel_from_ais(
            ais_type=row['VesselType'],
            speed_kn=row['SOG'],
            length_m=row['Length']
        ),
        axis=1
    )

    # Calculate noise emissions
    print("\n🔊 Calculating 125 Hz noise emissions...")
    df['emission_125hz_dB'] = df.apply(
        lambda row: day19_calculate_125hz_emission(
            vessel_type=row['vessel_class'],
            speed_kn=row['SOG'],
            length_m=row['Length']
        ),
        axis=1
    )

    print("\n📊 Vessel Classification Summary:")
    print("=" * 60)
    class_counts = df['vessel_class'].value_counts()
    for vessel_type, count in class_counts.items():
        pct = count / len(df) * 100
        print(f"   {vessel_type:<20} {count:>8,} ({pct:>5.1f}%)")

    print(f"\n📊 Noise Emission Statistics:")
    print("=" * 60)
    print(f"   Mean:   {df['emission_125hz_dB'].mean():.1f} dB re 1 µPa @ 1m")
    print(f"   Median: {df['emission_125hz_dB'].median():.1f} dB")
    print(f"   Range:  {df['emission_125hz_dB'].min():.1f} - {df['emission_125hz_dB'].max():.1f} dB")

    return df


def day19_create_grid_data(df, cell_size_deg=0.025):
    """
    Aggregate vessel positions into spatial grid cells.

    Args:
        df: DataFrame with vessel positions and noise data
        cell_size_deg: Grid cell size in degrees (~2.5km at equator for 0.025)

    Returns:
        pd.DataFrame: Grid cells with aggregated noise metrics
    """
    print(f"\n🗺️ Creating spatial grid (cell size: {cell_size_deg}° ≈ 2.5km)...")

    # Create grid cell IDs
    df['grid_lon'] = (df['LON'] // cell_size_deg) * cell_size_deg
    df['grid_lat'] = (df['LAT'] // cell_size_deg) * cell_size_deg
    df['cell_id'] = df['grid_lon'].astype(str) + '_' + df['grid_lat'].astype(str)

    # Aggregate by grid cell
    grid_agg = df.groupby(['grid_lon', 'grid_lat', 'cell_id']).agg({
        'emission_125hz_dB': ['mean', 'median', 'min', 'max', 'std'],
        'vessel_class': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Other',
        'MMSI': 'count'
    }).reset_index()

    # Flatten column names
    grid_agg.columns = [
        'grid_lon', 'grid_lat', 'cell_id',
        'noise_mean', 'noise_median', 'noise_min', 'noise_max', 'noise_std',
        'dominant_vessel_type', 'vessel_count'
    ]

    # Calculate cell center coordinates
    grid_agg['center_lon'] = grid_agg['grid_lon'] + cell_size_deg / 2
    grid_agg['center_lat'] = grid_agg['grid_lat'] + cell_size_deg / 2

    print(f"   ✅ Created {len(grid_agg):,} grid cells")
    print(f"   ✅ Cells with data: {(grid_agg['vessel_count'] > 0).sum():,}")

    return grid_agg


def day19_save_processed_data(df_vessels, df_grid):
    """Save processed data to day19/data/processed/ directory."""

    print(f"\n💾 Saving processed data to {PROCESSED_DIR}...")

    # Save vessel positions (sample for map markers)
    vessel_sample = df_vessels.sample(min(500, len(df_vessels)), random_state=42)
    vessel_file = PROCESSED_DIR / 'vessel_positions_sample.csv'
    vessel_sample.to_csv(vessel_file, index=False)
    print(f"   ✅ Saved vessel sample: {vessel_file.name} ({len(vessel_sample)} records)")

    # Save grid data
    grid_file = PROCESSED_DIR / 'grid_noise_gulf_of_mexico.csv'
    df_grid.to_csv(grid_file, index=False)
    print(f"   ✅ Saved grid data: {grid_file.name} ({len(df_grid)} cells)")

    # Save metadata
    metadata = {
        "data_source": "NOAA AIS - Gulf of Mexico (copied from GIS_SymphonyLayer)",
        "data_location": "day19/data/processed/",
        "time_period": "2024-01-01 (demonstration data)",
        "grid_resolution": "~2.5km x 2.5km (0.025 degrees)",
        "noise_model": "JOMOPANS-ECHO (125 Hz)",
        "vessel_count_total": int(df_vessels['MMSI'].nunique()),
        "vessel_records": len(df_vessels),
        "grid_cells_active": int((df_grid['vessel_count'] > 0).sum()),
        "source_project": "GIS_SymphonyLayer (methodology copied to day19/)",
        "self_contained": True
    }

    metadata_file = PROJECT_ROOT / 'day19_MAP_metadata.json'
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"   ✅ Saved metadata: {metadata_file.name}")

    return vessel_file, grid_file, metadata_file


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("DAY 19 - MARITIME NOISE DATA PREPARATION")
    print("=" * 70)

    try:
        # Step 1: Load and process AIS data
        df_vessels = day19_load_ais_data(
            filename='AIS_2024_01_01.csv',
            sample_size=5000  # MVP constraint
        )

        # Step 2: Create spatial grid
        df_grid = day19_create_grid_data(df_vessels)

        # Step 3: Save processed data
        vessel_file, grid_file, metadata_file = day19_save_processed_data(
            df_vessels, df_grid
        )

        print("\n" + "=" * 70)
        print("✅ DATA PREPARATION COMPLETE!")
        print("=" * 70)
        print(f"\n📂 Output files:")
        print(f"   • {vessel_file}")
        print(f"   • {grid_file}")
        print(f"   • {metadata_file}")
        print(f"\n🎯 Ready for visualization!")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise
