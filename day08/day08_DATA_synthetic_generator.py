"""
Day 08 - SaaS Growth Funnel & Cohort Analysis
Synthetic Data Generator for Patrick's Growth Strategy

Generates:
- 10K users with signup tracking
- 100K events across funnel stages
- Subscription data for paid conversions
"""

import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add common modules to path
sys.path.append(str(Path(__file__).parent.parent / 'common'))

try:
    from day08_CONFIG_settings import (
        DAY08_DB_PATH,
        DAY08_NUM_USERS,
        DAY08_NUM_EVENTS,
        DAY08_FUNNEL_STAGES,
        DAY08_UTM_SOURCES,
        DAY08_UTM_CAMPAIGNS,
        DAY08_FEATURE_NAMES,
        DAY08_ACTIVATION_THRESHOLD_DAYS
    )
except ImportError:
    # Fallback defaults if config not available
    DAY08_DB_PATH = "data/day08_saas_funnel.db"
    DAY08_NUM_USERS = 10000
    DAY08_NUM_EVENTS = 100000
    DAY08_FUNNEL_STAGES = ['visit', 'signup', 'activated', 'paid']
    DAY08_UTM_SOURCES = ['google', 'facebook', 'linkedin', 'twitter', 'organic', 'referral']
    DAY08_UTM_CAMPAIGNS = ['summer_2024', 'product_launch', 'webinar', 'content_marketing', 'retargeting']
    DAY08_FEATURE_NAMES = ['dashboard', 'reports', 'integrations', 'api', 'mobile_app', 'export']
    DAY08_ACTIVATION_THRESHOLD_DAYS = 7


class Day08_SaaSFunnelGenerator:
    """Generate synthetic SaaS funnel data for growth analysis"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self.start_date = datetime(2023, 1, 1)
        self.end_date = datetime(2024, 12, 31)

    def day08_setup_database(self):
        """Create database and tables"""
        print(f"Setting up database at {self.db_path}...")

        # Ensure data directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()

        # Drop existing tables
        cursor.execute("DROP TABLE IF EXISTS raw_events")
        cursor.execute("DROP TABLE IF EXISTS raw_subscriptions")
        cursor.execute("DROP TABLE IF EXISTS raw_users")

        # Create raw_users table
        cursor.execute("""
            CREATE TABLE raw_users (
                user_id TEXT PRIMARY KEY,
                signup_date DATE NOT NULL,
                email TEXT NOT NULL,
                utm_source TEXT,
                utm_campaign TEXT,
                first_visit_date DATE
            )
        """)

        # Create raw_events table
        cursor.execute("""
            CREATE TABLE raw_events (
                event_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_date DATE NOT NULL,
                event_timestamp TIMESTAMP NOT NULL,
                feature_name TEXT,
                FOREIGN KEY (user_id) REFERENCES raw_users(user_id)
            )
        """)

        # Create raw_subscriptions table
        cursor.execute("""
            CREATE TABLE raw_subscriptions (
                subscription_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                plan_name TEXT NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE,
                mrr REAL NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('active', 'cancelled', 'trial')),
                FOREIGN KEY (user_id) REFERENCES raw_users(user_id)
            )
        """)

        self.conn.commit()
        print("Database tables created successfully.")

    def day08_generate_users(self):
        """Generate synthetic users"""
        print(f"Generating {DAY08_NUM_USERS} users...")

        cursor = self.conn.cursor()
        users_data = []

        for i in range(DAY08_NUM_USERS):
            user_id = f"user_{i+1:06d}"

            # Random signup date between start and end date
            days_range = (self.end_date - self.start_date).days
            signup_offset = random.randint(0, days_range)
            signup_date = self.start_date + timedelta(days=signup_offset)

            # First visit is 0-7 days before signup
            first_visit_offset = random.randint(0, 7)
            first_visit_date = signup_date - timedelta(days=first_visit_offset)

            email = f"user{i+1}@example.com"
            utm_source = random.choice(DAY08_UTM_SOURCES)
            utm_campaign = random.choice(DAY08_UTM_CAMPAIGNS)

            users_data.append((
                user_id,
                signup_date.strftime('%Y-%m-%d'),
                email,
                utm_source,
                utm_campaign,
                first_visit_date.strftime('%Y-%m-%d')
            ))

        cursor.executemany("""
            INSERT INTO raw_users (user_id, signup_date, email, utm_source, utm_campaign, first_visit_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, users_data)

        self.conn.commit()
        print(f"Generated {len(users_data)} users.")

    def day08_generate_events(self):
        """Generate synthetic events across the funnel"""
        print(f"Generating {DAY08_NUM_EVENTS} events...")

        cursor = self.conn.cursor()

        # Get all users
        cursor.execute("SELECT user_id, signup_date, first_visit_date FROM raw_users")
        users = cursor.fetchall()

        events_data = []
        event_counter = 0

        for user_id, signup_date_str, first_visit_date_str in users:
            signup_date = datetime.strptime(signup_date_str, '%Y-%m-%d')
            first_visit_date = datetime.strptime(first_visit_date_str, '%Y-%m-%d')

            # 1. Visit event (everyone has at least one visit)
            visit_timestamp = first_visit_date + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
            events_data.append((
                f"event_{event_counter:08d}",
                user_id,
                'visit',
                first_visit_date.strftime('%Y-%m-%d'),
                visit_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                None
            ))
            event_counter += 1

            # 2. Signup event (everyone signed up)
            signup_timestamp = signup_date + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
            events_data.append((
                f"event_{event_counter:08d}",
                user_id,
                'signup',
                signup_date.strftime('%Y-%m-%d'),
                signup_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                None
            ))
            event_counter += 1

            # 3. Activation event (70% activate within threshold)
            if random.random() < 0.70:
                activation_days = random.randint(0, DAY08_ACTIVATION_THRESHOLD_DAYS)
                activation_date = signup_date + timedelta(days=activation_days)
                activation_timestamp = activation_date + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))

                events_data.append((
                    f"event_{event_counter:08d}",
                    user_id,
                    'activated',
                    activation_date.strftime('%Y-%m-%d'),
                    activation_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    None
                ))
                event_counter += 1

                # 4. Paid conversion event (30% of activated users convert)
                if random.random() < 0.30:
                    paid_days = random.randint(1, 14)
                    paid_date = activation_date + timedelta(days=paid_days)
                    paid_timestamp = paid_date + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))

                    events_data.append((
                        f"event_{event_counter:08d}",
                        user_id,
                        'paid',
                        paid_date.strftime('%Y-%m-%d'),
                        paid_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        None
                    ))
                    event_counter += 1

                    # 5. Engagement events for paid users (DAU, feature usage)
                    # Generate 5-15 engagement events per paid user
                    num_engagement_events = random.randint(5, 15)

                    for _ in range(num_engagement_events):
                        if event_counter >= DAY08_NUM_EVENTS:
                            break

                        # Random date after paid conversion
                        days_after_paid = random.randint(1, 90)
                        event_date = paid_date + timedelta(days=days_after_paid)

                        if event_date > self.end_date:
                            continue

                        event_timestamp = event_date + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))

                        # Mix of daily_active and feature_used events
                        event_type = random.choice(['daily_active', 'feature_used'])
                        feature_name = random.choice(DAY08_FEATURE_NAMES) if event_type == 'feature_used' else None

                        events_data.append((
                            f"event_{event_counter:08d}",
                            user_id,
                            event_type,
                            event_date.strftime('%Y-%m-%d'),
                            event_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                            feature_name
                        ))
                        event_counter += 1

            if event_counter >= DAY08_NUM_EVENTS:
                break

        cursor.executemany("""
            INSERT INTO raw_events (event_id, user_id, event_type, event_date, event_timestamp, feature_name)
            VALUES (?, ?, ?, ?, ?, ?)
        """, events_data)

        self.conn.commit()
        print(f"Generated {len(events_data)} events.")

    def day08_generate_subscriptions(self):
        """Generate subscription records for paid users"""
        print("Generating subscriptions...")

        cursor = self.conn.cursor()

        # Get users who have paid events
        cursor.execute("""
            SELECT DISTINCT u.user_id, e.event_date
            FROM raw_users u
            JOIN raw_events e ON u.user_id = e.user_id
            WHERE e.event_type = 'paid'
        """)
        paid_users = cursor.fetchall()

        subscriptions_data = []
        plan_options = [
            ('Starter', 29.0),
            ('Pro', 99.0),
            ('Enterprise', 299.0)
        ]

        for idx, (user_id, start_date_str) in enumerate(paid_users):
            subscription_id = f"sub_{idx+1:06d}"
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')

            plan_name, mrr = random.choice(plan_options)

            # 85% active, 10% cancelled, 5% trial
            status_roll = random.random()
            if status_roll < 0.85:
                status = 'active'
                end_date = None
            elif status_roll < 0.95:
                status = 'cancelled'
                # Cancelled 1-6 months after start
                end_date = start_date + timedelta(days=random.randint(30, 180))
                end_date = end_date.strftime('%Y-%m-%d')
            else:
                status = 'trial'
                end_date = None

            subscriptions_data.append((
                subscription_id,
                user_id,
                plan_name,
                start_date.strftime('%Y-%m-%d'),
                end_date,
                mrr,
                status
            ))

        cursor.executemany("""
            INSERT INTO raw_subscriptions (subscription_id, user_id, plan_name, start_date, end_date, mrr, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, subscriptions_data)

        self.conn.commit()
        print(f"Generated {len(subscriptions_data)} subscriptions.")

    def day08_print_summary(self):
        """Print summary statistics"""
        cursor = self.conn.cursor()

        print("\n" + "="*60)
        print("DATA GENERATION SUMMARY")
        print("="*60)

        # Users count
        cursor.execute("SELECT COUNT(*) FROM raw_users")
        user_count = cursor.fetchone()[0]
        print(f"Total Users: {user_count:,}")

        # Events by type
        cursor.execute("""
            SELECT event_type, COUNT(*) as count
            FROM raw_events
            GROUP BY event_type
            ORDER BY count DESC
        """)
        print("\nEvents by Type:")
        for event_type, count in cursor.fetchall():
            print(f"  {event_type}: {count:,}")

        # Total events
        cursor.execute("SELECT COUNT(*) FROM raw_events")
        event_count = cursor.fetchone()[0]
        print(f"  TOTAL: {event_count:,}")

        # Subscriptions by status
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM raw_subscriptions
            GROUP BY status
            ORDER BY count DESC
        """)
        print("\nSubscriptions by Status:")
        for status, count in cursor.fetchall():
            print(f"  {status}: {count:,}")

        # Total subscriptions
        cursor.execute("SELECT COUNT(*) FROM raw_subscriptions")
        sub_count = cursor.fetchone()[0]
        print(f"  TOTAL: {sub_count:,}")

        # Funnel conversion rates
        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM raw_events WHERE event_type = 'visit'")
        visitors = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM raw_events WHERE event_type = 'signup'")
        signups = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM raw_events WHERE event_type = 'activated'")
        activated = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM raw_events WHERE event_type = 'paid'")
        paid = cursor.fetchone()[0]

        print("\nFunnel Conversion Rates:")
        print(f"  Visitors: {visitors:,}")
        print(f"  Signups: {signups:,} ({100*signups/visitors:.1f}%)")
        print(f"  Activated: {activated:,} ({100*activated/signups:.1f}%)")
        print(f"  Paid: {paid:,} ({100*paid/activated:.1f}%)")

        print("="*60)

    def day08_generate_all(self):
        """Run complete data generation pipeline"""
        try:
            self.day08_setup_database()
            self.day08_generate_users()
            self.day08_generate_events()
            self.day08_generate_subscriptions()
            self.day08_print_summary()

            print(f"\nDatabase created successfully at: {self.db_path}")
            print("Ready for dbt modeling!")

        except Exception as e:
            print(f"Error during data generation: {e}")
            raise
        finally:
            if self.conn:
                self.conn.close()


def main():
    """Main entry point"""
    generator = Day08_SaaSFunnelGenerator(DAY08_DB_PATH)
    generator.day08_generate_all()


if __name__ == "__main__":
    main()
