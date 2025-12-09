"""
Day 09 Synthetic Data Generator
Property Manager Operations Data Warehouse

Generates realistic multi-platform property management data:
- Airbnb inquiries & bookings
- Booking.com inquiries & bookings (following OTA schema conventions)
- Unified stays & reviews

Simulates Jo's 6 houseboats with realistic conversion funnels.
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from day09_CONFIG_settings import *

# Set random seed for reproducibility
random.seed(DAY09_RANDOM_SEED)
np.random.seed(DAY09_RANDOM_SEED)


class day09_PropertyDataGenerator:
    """Generate synthetic property management data across platforms"""

    def __init__(self):
        self.db_path = DAY09_DB_PATH
        day09_ensure_data_dir()
        self.properties = DAY09_PROPERTIES
        self.platforms = DAY09_PLATFORMS
        self.start_date = datetime.strptime(DAY09_START_DATE, "%Y-%m-%d")
        self.end_date = datetime.strptime(DAY09_END_DATE, "%Y-%m-%d")

    def day09_generate_guest_names(self, n):
        """Generate realistic guest names"""
        first_names = ["Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason",
                       "Isabella", "Logan", "Mia", "Lucas", "Charlotte", "Oliver", "Amelia"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
                      "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez"]

        return [f"{random.choice(first_names)} {random.choice(last_names)}" for _ in range(n)]

    def day09_generate_inquiries(self, platform, num_inquiries):
        """Generate inquiries for a specific platform"""
        inquiries = []

        for i in range(num_inquiries):
            # Random inquiry date within range
            days_range = (self.end_date - self.start_date).days - 30  # Leave buffer for bookings
            inquiry_date = self.start_date + timedelta(days=random.randint(0, days_range))

            # Random property
            property_data = random.choice(self.properties)

            # Check-in: 3-45 days after inquiry
            check_in = inquiry_date + timedelta(days=random.randint(3, 45))

            # Stay duration: 2-7 nights typically
            nights = random.choices([2, 3, 4, 5, 6, 7], weights=[15, 25, 30, 15, 10, 5])[0]
            check_out = check_in + timedelta(days=nights)

            # Number of guests
            max_guests = property_data["capacity"]
            num_guests = random.randint(1, max_guests)

            # Platform-specific fields
            if platform == "airbnb":
                inquiry = {
                    "inquiry_id": f"AIR-INQ-{i+1:04d}",
                    "guest_id": f"airbnb_guest_{i+1:04d}",
                    "guest_name": self.day09_generate_guest_names(1)[0],
                    "property_id": property_data["id"],
                    "inquiry_timestamp": inquiry_date,
                    "check_in_date": check_in,
                    "check_out_date": check_out,
                    "num_guests": num_guests,
                    "status": random.choices(
                        ["pending", "responded", "expired"],
                        weights=[20, 60, 20]
                    )[0],
                }
            else:  # booking_com - following OTA schema conventions
                inquiry = {
                    "reservation_inquiry_id": f"BDC-INQ-{i+1:04d}",
                    "guest_email": f"guest_{i+1:04d}@email.com",
                    "guest_name": self.day09_generate_guest_names(1)[0],
                    "property_code": property_data["id"],
                    "created_at": inquiry_date,
                    "arrival_date": check_in,
                    "departure_date": check_out,
                    "guest_count": num_guests,
                    "inquiry_status": random.choices(
                        ["pending", "responded", "expired"],
                        weights=[20, 60, 20]
                    )[0],
                }

            inquiries.append(inquiry)

        return pd.DataFrame(inquiries)

    def day09_generate_bookings_from_inquiries(self, inquiries_df, platform):
        """Convert inquiries to bookings based on conversion rate"""
        # Select inquiries that convert to bookings
        conversion_rate = DAY09_CONVERSION_RATES["inquiry_to_booking"]
        num_bookings = int(len(inquiries_df) * conversion_rate)

        # Sample inquiries that convert
        booking_inquiries = inquiries_df.sample(n=num_bookings, random_state=DAY09_RANDOM_SEED)

        bookings = []

        for idx, inq in booking_inquiries.iterrows():
            # Get property info
            if platform == "airbnb":
                property_id = inq["property_id"]
                check_in = inq["check_in_date"]
                check_out = inq["check_out_date"]
                num_guests = inq["num_guests"]
                guest_id = inq["guest_id"]
            else:  # booking_com
                property_id = inq["property_code"]
                check_in = inq["arrival_date"]
                check_out = inq["departure_date"]
                num_guests = inq["guest_count"]
                guest_id = inq["guest_email"]

            property_data = next(p for p in self.properties if p["id"] == property_id)

            # Calculate pricing
            nights = (check_out - check_in).days
            base_price = property_data["base_price"]

            # Add seasonality (summer prices +20%, winter -10%)
            month = check_in.month
            if month in [6, 7, 8]:  # Summer
                price_multiplier = 1.2
            elif month in [12, 1, 2]:  # Winter
                price_multiplier = 0.9
            else:
                price_multiplier = 1.0

            nightly_rate = base_price * price_multiplier
            total_price = nightly_rate * nights

            # Platform fee
            platform_fee_rate = DAY09_PLATFORM_FEES[platform]
            platform_fee = total_price * platform_fee_rate
            net_revenue = total_price - platform_fee

            # Booking timestamp: 1-3 days after inquiry
            inquiry_ts = inq["inquiry_timestamp"] if platform == "airbnb" else inq["created_at"]
            booking_ts = inquiry_ts + timedelta(days=random.randint(1, 3))

            # Booking status (most are confirmed, some cancelled)
            booking_status = random.choices(
                ["confirmed", "cancelled", "completed"],
                weights=[85, 5, 10]
            )[0]

            if platform == "airbnb":
                booking = {
                    "booking_id": f"AIR-BKG-{len(bookings)+1:04d}",
                    "guest_id": guest_id,
                    "property_id": property_id,
                    "booking_timestamp": booking_ts,
                    "check_in_date": check_in,
                    "check_out_date": check_out,
                    "num_guests": num_guests,
                    "nights": nights,
                    "nightly_rate": round(nightly_rate, 2),
                    "total_price": round(total_price, 2),
                    "platform_fee": round(platform_fee, 2),
                    "net_revenue": round(net_revenue, 2),
                    "status": booking_status,
                }
            else:  # booking_com - OTA schema conventions
                booking = {
                    "booking_id": f"BDC-BKG-{len(bookings)+1:04d}",
                    "guest_email": guest_id,
                    "property_code": property_id,
                    "booking_timestamp": booking_ts,
                    "arrival_date": check_in,
                    "departure_date": check_out,
                    "guest_count": num_guests,
                    "nights": nights,
                    "rate_per_night": round(nightly_rate, 2),
                    "total_amount": round(total_price, 2),
                    "commission": round(platform_fee, 2),
                    "host_payout": round(net_revenue, 2),
                    "booking_status": booking_status,
                }

            bookings.append(booking)

        return pd.DataFrame(bookings)

    def day09_generate_stays(self, airbnb_bookings, booking_com_bookings):
        """Generate unified stays from confirmed bookings"""
        stays = []

        # Combine bookings from both platforms
        all_bookings = []

        # Airbnb bookings
        for idx, booking in airbnb_bookings.iterrows():
            if booking["status"] in ["confirmed", "completed"]:
                all_bookings.append({
                    "platform": "airbnb",
                    "booking_id": booking["booking_id"],
                    "property_id": booking["property_id"],
                    "guest_id": booking["guest_id"],
                    "check_in_date": booking["check_in_date"],
                    "check_out_date": booking["check_out_date"],
                    "num_guests": booking["num_guests"],
                })

        # Booking.com bookings
        for idx, booking in booking_com_bookings.iterrows():
            if booking["booking_status"] in ["confirmed", "completed"]:
                all_bookings.append({
                    "platform": "booking_com",
                    "booking_id": booking["booking_id"],
                    "property_id": booking["property_code"],
                    "guest_id": booking["guest_email"],
                    "check_in_date": booking["arrival_date"],
                    "check_out_date": booking["departure_date"],
                    "num_guests": booking["guest_count"],
                })

        # Generate stays (92% actually check in)
        num_stays = int(len(all_bookings) * DAY09_CONVERSION_RATES["booking_to_check_in"])
        stay_bookings = random.sample(all_bookings, num_stays)

        for i, booking in enumerate(stay_bookings):
            # Check-in time (usually 3-5 PM)
            check_in_time = booking["check_in_date"] + timedelta(hours=random.randint(15, 17))

            # Check-out time (usually 10-11 AM)
            check_out_time = booking["check_out_date"] + timedelta(hours=random.randint(10, 11))

            # 98% complete the stay successfully
            stay_completed = random.random() < DAY09_CONVERSION_RATES["check_in_to_check_out"]

            stay = {
                "stay_id": f"STAY-{i+1:04d}",
                "booking_id": booking["booking_id"],
                "platform": booking["platform"],
                "property_id": booking["property_id"],
                "guest_id": booking["guest_id"],
                "check_in_timestamp": check_in_time,
                "check_out_timestamp": check_out_time if stay_completed else None,
                "num_guests": booking["num_guests"],
                "stay_status": "completed" if stay_completed else "early_departure",
            }

            stays.append(stay)

        return pd.DataFrame(stays)

    def day09_generate_reviews(self, stays_df):
        """Generate reviews from completed stays"""
        reviews = []

        # Only completed stays get reviews, 35% leave reviews
        completed_stays = stays_df[stays_df["stay_status"] == "completed"]
        num_reviews = int(len(completed_stays) * DAY09_CONVERSION_RATES["check_out_to_review"])

        review_stays = completed_stays.sample(n=num_reviews, random_state=DAY09_RANDOM_SEED)

        review_comments = [
            "Amazing property with beautiful views!",
            "Great location and very clean.",
            "Perfect getaway spot. Highly recommend!",
            "Comfortable and well-equipped.",
            "Host was very responsive and helpful.",
            "Exceeded our expectations!",
            "Would definitely stay again.",
            "Beautiful property but a bit remote.",
            "Great value for money.",
            "Perfect for a family vacation.",
        ]

        for i, (idx, stay) in enumerate(review_stays.iterrows()):
            # Review submitted 1-7 days after checkout
            review_date = stay["check_out_timestamp"] + timedelta(days=random.randint(1, 7))

            # Rating (skewed toward positive)
            rating = round(np.clip(
                np.random.normal(DAY09_AVG_RATING, DAY09_RATING_STDDEV),
                1, 5
            ), 1)

            review = {
                "review_id": f"REV-{i+1:04d}",
                "stay_id": stay["stay_id"],
                "booking_id": stay["booking_id"],
                "platform": stay["platform"],
                "property_id": stay["property_id"],
                "guest_id": stay["guest_id"],
                "review_timestamp": review_date,
                "rating": rating,
                "comment": random.choice(review_comments),
            }

            reviews.append(review)

        return pd.DataFrame(reviews)

    def day09_create_database_tables(self, conn):
        """Create raw tables in SQLite database"""
        cursor = conn.cursor()

        # Airbnb Inquiries
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS airbnb_inquiries (
            inquiry_id TEXT PRIMARY KEY,
            guest_id TEXT,
            guest_name TEXT,
            property_id TEXT,
            inquiry_timestamp TIMESTAMP,
            check_in_date DATE,
            check_out_date DATE,
            num_guests INTEGER,
            status TEXT
        )
        """)

        # Airbnb Bookings
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS airbnb_bookings (
            booking_id TEXT PRIMARY KEY,
            guest_id TEXT,
            property_id TEXT,
            booking_timestamp TIMESTAMP,
            check_in_date DATE,
            check_out_date DATE,
            num_guests INTEGER,
            nights INTEGER,
            nightly_rate REAL,
            total_price REAL,
            platform_fee REAL,
            net_revenue REAL,
            status TEXT
        )
        """)

        # Booking.com Inquiries (OTA schema conventions)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS booking_com_inquiries (
            reservation_inquiry_id TEXT PRIMARY KEY,
            guest_email TEXT,
            guest_name TEXT,
            property_code TEXT,
            created_at TIMESTAMP,
            arrival_date DATE,
            departure_date DATE,
            guest_count INTEGER,
            inquiry_status TEXT
        )
        """)

        # Booking.com Bookings (OTA schema conventions)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS booking_com_bookings (
            booking_id TEXT PRIMARY KEY,
            guest_email TEXT,
            property_code TEXT,
            booking_timestamp TIMESTAMP,
            arrival_date DATE,
            departure_date DATE,
            guest_count INTEGER,
            nights INTEGER,
            rate_per_night REAL,
            total_amount REAL,
            commission REAL,
            host_payout REAL,
            booking_status TEXT
        )
        """)

        # Unified Stays
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS stays (
            stay_id TEXT PRIMARY KEY,
            booking_id TEXT,
            platform TEXT,
            property_id TEXT,
            guest_id TEXT,
            check_in_timestamp TIMESTAMP,
            check_out_timestamp TIMESTAMP,
            num_guests INTEGER,
            stay_status TEXT
        )
        """)

        # Unified Reviews
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            review_id TEXT PRIMARY KEY,
            stay_id TEXT,
            booking_id TEXT,
            platform TEXT,
            property_id TEXT,
            guest_id TEXT,
            review_timestamp TIMESTAMP,
            rating REAL,
            comment TEXT
        )
        """)

        conn.commit()
        print("✓ Database tables created successfully")

    def day09_generate_all_data(self):
        """Main method to generate all synthetic data"""
        print("=" * 60)
        print("Day 09: Property Management Data Generator")
        print("=" * 60)
        print(f"Properties: {len(self.properties)}")
        print(f"Platforms: {', '.join(self.platforms)}")
        print(f"Date Range: {self.start_date.date()} to {self.end_date.date()}")
        print()

        # Split inquiries between platforms (60% Airbnb, 40% Booking.com)
        num_airbnb_inquiries = int(DAY09_NUM_INQUIRIES * 0.6)
        num_booking_com_inquiries = DAY09_NUM_INQUIRIES - num_airbnb_inquiries

        print(f"Generating {num_airbnb_inquiries} Airbnb inquiries...")
        airbnb_inquiries = self.day09_generate_inquiries("airbnb", num_airbnb_inquiries)

        print(f"Generating {num_booking_com_inquiries} Booking.com inquiries...")
        booking_com_inquiries = self.day09_generate_inquiries("booking_com", num_booking_com_inquiries)

        print("Generating Airbnb bookings...")
        airbnb_bookings = self.day09_generate_bookings_from_inquiries(airbnb_inquiries, "airbnb")

        print("Generating Booking.com bookings...")
        booking_com_bookings = self.day09_generate_bookings_from_inquiries(booking_com_inquiries, "booking_com")

        print("Generating stays...")
        stays = self.day09_generate_stays(airbnb_bookings, booking_com_bookings)

        print("Generating reviews...")
        reviews = self.day09_generate_reviews(stays)

        print()
        print("Data Generation Summary:")
        print("-" * 60)
        print(f"Airbnb Inquiries: {len(airbnb_inquiries)}")
        print(f"Airbnb Bookings: {len(airbnb_bookings)}")
        print(f"Booking.com Inquiries: {len(booking_com_inquiries)}")
        print(f"Booking.com Bookings: {len(booking_com_bookings)}")
        print(f"Total Stays: {len(stays)}")
        print(f"Total Reviews: {len(reviews)}")
        print()

        # Create database and load data
        print("Creating database and loading data...")
        conn = sqlite3.connect(self.db_path)

        self.day09_create_database_tables(conn)

        # Load data into tables
        airbnb_inquiries.to_sql("airbnb_inquiries", conn, if_exists="replace", index=False)
        airbnb_bookings.to_sql("airbnb_bookings", conn, if_exists="replace", index=False)
        booking_com_inquiries.to_sql("booking_com_inquiries", conn, if_exists="replace", index=False)
        booking_com_bookings.to_sql("booking_com_bookings", conn, if_exists="replace", index=False)
        stays.to_sql("stays", conn, if_exists="replace", index=False)
        reviews.to_sql("reviews", conn, if_exists="replace", index=False)

        conn.close()

        print(f"✓ Database created successfully at: {self.db_path}")
        print()

        # Display sample metrics
        self.day09_display_sample_metrics(airbnb_bookings, booking_com_bookings)

        return {
            "airbnb_inquiries": airbnb_inquiries,
            "airbnb_bookings": airbnb_bookings,
            "booking_com_inquiries": booking_com_inquiries,
            "booking_com_bookings": booking_com_bookings,
            "stays": stays,
            "reviews": reviews,
        }

    def day09_display_sample_metrics(self, airbnb_bookings, booking_com_bookings):
        """Display sample metrics for validation"""
        print("Sample Metrics:")
        print("-" * 60)

        # Combine bookings for metrics
        all_completed_bookings = []

        for _, booking in airbnb_bookings[airbnb_bookings["status"] == "completed"].iterrows():
            all_completed_bookings.append({
                "platform": "airbnb",
                "property_id": booking["property_id"],
                "nights": booking["nights"],
                "total_price": booking["total_price"],
                "net_revenue": booking["net_revenue"],
            })

        for _, booking in booking_com_bookings[booking_com_bookings["booking_status"] == "completed"].iterrows():
            all_completed_bookings.append({
                "platform": "booking_com",
                "property_id": booking["property_code"],
                "nights": booking["nights"],
                "total_price": booking["total_amount"],
                "net_revenue": booking["host_payout"],
            })

        if all_completed_bookings:
            df_metrics = pd.DataFrame(all_completed_bookings)

            # Total revenue
            total_revenue = df_metrics["total_price"].sum()
            total_net_revenue = df_metrics["net_revenue"].sum()

            # Average Daily Rate (ADR)
            total_nights = df_metrics["nights"].sum()
            adr = total_revenue / total_nights if total_nights > 0 else 0

            # Platform split
            platform_revenue = df_metrics.groupby("platform")["total_price"].sum()

            print(f"Total Gross Revenue: ${total_revenue:,.2f}")
            print(f"Total Net Revenue: ${total_net_revenue:,.2f}")
            print(f"Average Daily Rate (ADR): ${adr:.2f}")
            print(f"Total Nights Booked: {total_nights}")
            print()
            print("Revenue by Platform:")
            for platform, revenue in platform_revenue.items():
                pct = (revenue / total_revenue * 100) if total_revenue > 0 else 0
                print(f"  {platform}: ${revenue:,.2f} ({pct:.1f}%)")

        print()
        print("=" * 60)


if __name__ == "__main__":
    generator = day09_PropertyDataGenerator()
    data = generator.day09_generate_all_data()

    print("✓ Data generation complete!")
    print()
    print("Next steps:")
    print("1. Run: cd day09 && dbt run --full-refresh")
    print("2. Run tests: dbt test")
    print("3. Generate docs: dbt docs generate && dbt docs serve")
