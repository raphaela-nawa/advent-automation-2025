"""
IBA Climate Registry Web Scraper
Extracts resources and metadata from the public registry
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
from collections import Counter

class RegistryScraper:
    def __init__(self):
        self.base_url = "https://www.ibanet.org/IBA-Climate-Registry"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        # Region to countries mapping (matched to IBA Registry region names)
        self.region_countries = {
            'Africa': ['nigeria', 'south africa', 'kenya', 'ghana', 'uganda', 'tanzania', 'zambia', 'zimbabwe', 'botswana', 'namibia', 'malawi', 'mozambique', 'angola', 'ethiopia'],
            'Middle East and North Africa (MENA)': ['egypt', 'morocco', 'tunisia', 'algeria', 'libya', 'sudan', 'uae', 'dubai', 'saudi', 'qatar', 'kuwait', 'bahrain', 'oman', 'israel', 'palestine', 'jordan', 'lebanon', 'turkey', 'iran', 'iraq', 'yemen', 'syria'],
            'Asia': ['japan', 'china', 'india', 'singapore', 'hong kong', 'south korea', 'korea', 'thailand', 'malaysia', 'indonesia', 'philippines', 'vietnam', 'pakistan', 'bangladesh', 'sri lanka', 'taiwan', 'mongolia', 'cambodia', 'myanmar', 'nepal', 'laos'],
            'Europe': ['uk', 'united kingdom', 'england', 'scotland', 'wales', 'northern ireland', 'britain', 'france', 'germany', 'spain', 'italy', 'netherlands', 'belgium', 'sweden', 'norway', 'denmark', 'finland', 'poland', 'portugal', 'austria', 'switzerland', 'ireland', 'greece', 'czech', 'hungary', 'romania', 'croatia', 'slovenia', 'slovakia', 'bulgaria', 'luxembourg', 'estonia', 'latvia', 'lithuania', 'iceland', 'malta', 'cyprus'],
            'Central and South America (LATAM)': ['brazil', 'brasil', 'oab', 'mexico', 'argentina', 'chile', 'colombia', 'peru', 'venezuela', 'ecuador', 'bolivia', 'paraguay', 'uruguay', 'costa rica', 'panama', 'guatemala', 'honduras', 'el salvador', 'nicaragua', 'cuba', 'dominican', 'puerto rico', 'guyana', 'suriname'],
            'North America': ['usa', 'united states', 'america', 'canada', 'american', 'canadian', 'us ', 'aba', 'american bar'],
            'Oceania': ['australia', 'new zealand', 'fiji', 'papua', 'samoa', 'tonga', 'vanuatu', 'solomon', 'australian', 'law council of australia'],
            'International': ['international', 'global', 'worldwide', 'ccbe', 'council of bars', 'iba', 'iba net']
        }

    def fetch_page(self):
        """Fetch the registry page"""
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching page: {e}")
            return None

    def extract_country(self, text, region):
        """
        Extract country from text based on keywords
        Returns country name or 'International' if not found
        """
        text_lower = text.lower()

        # Check each country in the region
        if region in self.region_countries:
            for country in self.region_countries[region]:
                if country in text_lower:
                    return country.title()

        # Check International keywords
        for keyword in self.region_countries['International']:
            if keyword in text_lower:
                return 'International'

        return 'Unknown'

    def parse_regional_accordion(self, soup):
        """
        Extract bar association submissions from regional accordion
        Returns: List of dicts with {title, url, region, country, type}
        """
        resources = []

        # Target: div#menu1 > div#accordion
        menu1 = soup.find('div', id='menu1')
        if not menu1:
            print("⚠️  Warning: div#menu1 not found")
            return resources

        accordion = menu1.find('div', id='accordion', class_='accordion-component')
        if not accordion:
            print("⚠️  Warning: Regional accordion not found")
            return resources

        cards = accordion.find_all('div', class_='card')
        print(f"📊 Found {len(cards)} regional cards")

        for card in cards:
            # Extract region name from card-header button text
            header = card.find('div', class_='card-header')
            if not header:
                continue

            button = header.find('button')
            region_name = button.get_text(strip=True) if button else "Unknown"

            # Extract resources from panel-body
            panel_body = card.find('div', class_='panel-body')
            if not panel_body:
                continue

            # Find all links in this region
            links = panel_body.find_all('a', href=True)

            # Track contact info for grouping
            last_contact_name = None

            for link in links:
                href = link.get('href')
                title = link.get_text(strip=True)

                # Handle mailto links specially
                if href.startswith('mailto:'):
                    # Extract contact name from previous element if available
                    contact_name = last_contact_name or "Contact"

                    # Get surrounding context for country detection
                    context = panel_body.get_text()
                    country = self.extract_country(context, region_name)

                    resources.append({
                        'title': title,
                        'url': href,
                        'region': region_name,
                        'country': country,
                        'type': 'contact_email',
                        'contact_name': contact_name,
                        'source': 'regional_submission'
                    })
                    continue

                # Check if this might be a contact name (for next mailto)
                if '@' not in title and len(title) > 5 and not href.startswith('http'):
                    last_contact_name = title

                # Validate resource
                if not self.is_valid_resource(title, href):
                    continue

                # Make URL absolute if needed
                if href.startswith('/'):
                    href = f"https://www.ibanet.org{href}"

                # Extract country from title and URL
                country = self.extract_country(f"{title} {href}", region_name)

                resources.append({
                    'title': title,
                    'url': href,
                    'region': region_name,
                    'country': country,
                    'type': self._classify_resource(title, href),
                    'source': 'regional_submission'
                })

        return resources

    def parse_resources_accordion(self, soup):
        """
        Extract IBA-curated resources (tools and articles)
        Returns: List of dicts with {title, url, category, type}
        """
        resources = []

        # Try multiple selectors for the resources section
        # Approach 1: Look for heading with "Resources" text
        resources_heading = soup.find(['h2', 'h3', 'h4'], string=lambda text: text and 'resources' in text.lower() and 'climate' in text.lower())

        if resources_heading:
            print("📚 Found resources section via heading")
            # Get the next accordion after this heading
            accordion = resources_heading.find_next('div', class_='accordion-component')

            if accordion:
                cards = accordion.find_all('div', class_='card')
                print(f"📊 Found {len(cards)} resource category cards")

                for card in cards:
                    # Extract category from card-header button text
                    header = card.find('div', class_='card-header')
                    if not header:
                        continue

                    button = header.find('button')
                    category = button.get_text(strip=True) if button else "Unknown"

                    # Extract resources from panel-body
                    panel_body = card.find('div', class_='panel-body')
                    if not panel_body:
                        continue

                    # Find all links
                    links = panel_body.find_all('a', href=True)

                    for link in links:
                        href = link.get('href')
                        title = link.get_text(strip=True)

                        # Validate resource
                        if not self.is_valid_resource(title, href):
                            continue

                        # Make URL absolute if needed
                        if href.startswith('/'):
                            href = f"https://www.ibanet.org{href}"

                        # Description might be in adjacent <p> or text
                        description = ""
                        next_elem = link.find_next_sibling('p')
                        if next_elem:
                            description = next_elem.get_text(strip=True)[:200]

                        resources.append({
                            'title': title,
                            'url': href,
                            'category': category,
                            'country': 'International',
                            'description': description,
                            'type': self._classify_resource(title, href),
                            'source': 'iba_curated'
                        })
            else:
                print("⚠️  Warning: No accordion found after resources heading")
        else:
            print("⚠️  Warning: Resources heading not found")

        return resources

    def is_valid_resource(self, title, url):
        """
        Filter out navigation links and noise
        """
        if not title or not url:
            return False

        title_lower = title.lower()
        url_lower = url.lower()

        # Exclude patterns
        excluded = [
            'submit', 'click here', 'read more', 'share',
            'facebook', 'twitter', 'linkedin', 'instagram',
            'council members', 'contact us', 'about',
            'eyewitness', 'menu', 'navigation',
            'cookie', 'privacy', 'terms',
            'download pdf'  # when it's just a download link without context
        ]

        if any(pattern in title_lower for pattern in excluded):
            return False

        # Allow "read in [language]" if it's an IBA document link
        if title_lower.startswith('read in'):
            if '/document?id=' in url_lower or 'ibanet.org' in url_lower:
                return True  # Keep these - they're actual documents
            if len(title) < 20:
                return False  # Filter out generic "read in" links

        # Exclude internal navigation
        if url.startswith('#') or 'javascript:' in url_lower:
            return False

        # Exclude if title too short and not a PDF
        if len(title) < 10 and not url.endswith('.pdf'):
            return False

        return True

    def _classify_resource(self, title, url):
        """
        Classify resource based on title and URL keywords
        Priority order: litigation > policy > guidance > training > operational > article > other
        """
        text = f"{title} {url}".lower()

        # Check in priority order
        if any(kw in text for kw in ['litigation', 'court', 'case', 'advisory opinion', 'judgment', 'tribunal', 'icj', 'international court']):
            return 'litigation'

        if any(kw in text for kw in ['policy', 'statement', 'resolution', 'declaration', 'commitment', 'pledge', 'strategy', 'charter']):
            return 'policy'

        if any(kw in text for kw in ['guidance', 'guide', 'toolkit', 'framework', 'best practice', 'how-to', 'practitioner', 'recommendations', 'advising']):
            return 'guidance'

        if any(kw in text for kw in ['training', 'course', 'education', 'seminar', 'workshop', 'learning', 'lecture', 'webinar', 'curriculum']):
            return 'training'

        if any(kw in text for kw in ['carbon', 'footprint', 'net zero', 'emissions', 'calculator', 'measurement', 'sustainability strategy', 'csr report']):
            return 'operational'

        # Academic/research articles
        if any(kw in text for kw in ['article', 'paper', 'publication', 'journal', 'research', 'academic', 'author:', 'published']):
            return 'article'

        # Tools and databases
        if any(kw in text for kw in ['database', 'atlas', 'hub', 'portal', 'platform', 'tool', 'resource hub']):
            return 'tool'

        return 'other'

    def _generate_statistics(self, resources):
        """Generate summary statistics"""
        type_counts = Counter(r['type'] for r in resources)

        # Regional breakdown
        regional_counts = Counter(r.get('region', 'N/A') for r in resources if r.get('source') == 'regional_submission')

        # Country breakdown
        country_counts = Counter(r.get('country', 'Unknown') for r in resources)

        # Category breakdown
        category_counts = Counter(r.get('category', 'N/A') for r in resources if r.get('source') == 'iba_curated')

        return {
            'by_type': dict(type_counts),
            'by_region': dict(regional_counts),
            'by_country': dict(sorted(country_counts.items(), key=lambda x: x[1], reverse=True)),
            'by_category': dict(category_counts),
            'other_percentage': round(type_counts.get('other', 0) / len(resources) * 100, 1) if resources else 0
        }

    def scrape(self):
        """
        Main scraping method - updated to use new parsing functions
        """
        print("🔍 Fetching IBA Climate Registry...")
        html = self.fetch_page()

        if not html:
            return None

        soup = BeautifulSoup(html, 'html.parser')

        print("\n📋 Parsing regional submissions...")
        regional_resources = self.parse_regional_accordion(soup)
        print(f"   ✅ Found {len(regional_resources)} regional resources")

        print("\n📚 Parsing curated resources...")
        curated_resources = self.parse_resources_accordion(soup)
        print(f"   ✅ Found {len(curated_resources)} curated resources")

        # Combine and deduplicate
        all_resources = regional_resources + curated_resources

        # Remove duplicates based on URL
        seen_urls = set()
        unique_resources = []
        for resource in all_resources:
            if resource['url'] not in seen_urls:
                seen_urls.add(resource['url'])
                unique_resources.append(resource)

        if len(all_resources) != len(unique_resources):
            print(f"   ℹ️  Removed {len(all_resources) - len(unique_resources)} duplicates")

        # Generate statistics
        stats = self._generate_statistics(unique_resources)

        data = {
            'metadata': {
                'source': self.base_url,
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_resources': len(unique_resources),
                'regional_count': len(regional_resources),
                'curated_count': len(curated_resources)
            },
            'statistics': stats,
            'resources': unique_resources
        }

        return data

    def save_data(self, data, filename='day01_DATA_registry_raw.json'):
        """Save scraped data to JSON"""
        output_path = Path(__file__).parent / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✅ Data saved to {output_path}")
        return output_path

if __name__ == "__main__":
    scraper = RegistryScraper()
    data = scraper.scrape()

    if data:
        scraper.save_data(data)
        print(f"\n📊 Summary:")
        print(f"   - Total resources: {data['metadata']['total_resources']}")
        print(f"   - Regional submissions: {data['metadata']['regional_count']}")
        print(f"   - Curated resources: {data['metadata']['curated_count']}")
        print(f"\n🏷️  Classification:")
        for resource_type, count in sorted(data['statistics']['by_type'].items(), key=lambda x: x[1], reverse=True):
            print(f"   - {resource_type}: {count}")
        print(f"\n   Other percentage: {data['statistics']['other_percentage']}%")
    else:
        print("❌ Scraping failed")
