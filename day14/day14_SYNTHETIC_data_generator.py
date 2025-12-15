"""
Day 14: Synthetic Data Generator for Transport Regulatory KPIs

Generates realistic synthetic data mimicking Querido Diário API structure.
Used because Cloudflare blocks automated API access (403 Forbidden).

This demonstrates the complete workflow with realistic data patterns.
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List
from day14_CONFIG_settings import DAY14_TERRITORY_IDS, DAY14_KPI_DEFINITIONS


class Day14SyntheticDataGenerator:
    """Generate realistic synthetic gazette data."""

    # Realistic transport regulation topics (Portuguese)
    TRANSPORT_TOPICS = [
        "Regulamentação de transporte público municipal",
        "Alteração de itinerário de linhas de ônibus",
        "Licitação para concessão de transporte coletivo",
        "Criação de novas linhas de transporte",
        "Fiscalização de veículos de transporte escolar",
        "Implementação de faixas exclusivas para ônibus",
        "Regulamentação de aplicativos de transporte",
        "Normas de acessibilidade em veículos",
        "Política de mobilidade urbana sustentável",
        "Concessão de alvarás para táxis",
        "Regulamentação de estacionamento rotativo",
        "Implementação de ciclovias e ciclofaixas",
        "Normas de segurança viária",
        "Fiscalização de transporte irregular",
        "Subsídios para tarifa de transporte público"
    ]

    # Compliance-related terms
    COMPLIANCE_TERMS = [
        "prazo de 30 dias para adequação",
        "cumprimento das normas de segurança",
        "fiscalização será intensificada",
        "obrigatoriedade de licenciamento",
        "prazo estabelecido em regulamento",
        "responsabilização por descumprimento",
        "prazo final: 31 de dezembro",
        "fiscalização preventiva e corretiva"
    ]

    # Safety-related terms
    SAFETY_TERMS = [
        "acidente envolvendo transporte coletivo",
        "medidas de segurança viária reforçadas",
        "infração de trânsito com multa",
        "programa de segurança no trânsito",
        "redução de acidentes em 15%",
        "autuação por transporte irregular",
        "segurança de pedestres e ciclistas",
        "multa por excesso de velocidade"
    ]

    def __init__(self):
        self.cities = list(DAY14_TERRITORY_IDS.keys())

    def generate_gazette_excerpt(self, topic: str, include_compliance: bool = False,
                                 include_safety: bool = False) -> str:
        """Generate a realistic gazette excerpt."""
        base_text = f"{topic}. "

        # Add regulatory context
        contexts = [
            f"A Secretaria Municipal de Transportes estabelece novas diretrizes para {topic.lower()}.",
            f"Fica regulamentado no município de acordo com a Lei Municipal nº {random.randint(1000, 9999)}/2025.",
            f"O Departamento de Trânsito comunica à população sobre {topic.lower()}.",
            f"Decreto Municipal determina normas para {topic.lower()}."
        ]
        base_text += random.choice(contexts) + " "

        # Add compliance terms if requested
        if include_compliance and random.random() > 0.5:
            base_text += random.choice(self.COMPLIANCE_TERMS) + ". "

        # Add safety terms if requested
        if include_safety and random.random() > 0.5:
            base_text += random.choice(self.SAFETY_TERMS) + ". "

        # Add closing
        base_text += "Publicado no Diário Oficial do Município."

        return base_text

    def generate_gazette(self, city: str, date: str) -> Dict:
        """Generate a single gazette entry."""
        topic = random.choice(self.TRANSPORT_TOPICS)

        # Randomly decide if this gazette has compliance/safety mentions
        has_compliance = random.random() > 0.6
        has_safety = random.random() > 0.7

        excerpt = self.generate_gazette_excerpt(
            topic,
            include_compliance=has_compliance,
            include_safety=has_safety
        )

        return {
            "date": date,
            "edition": f"{random.randint(100, 999)}",
            "is_extra_edition": random.random() > 0.9,
            "state_code": "BR",
            "territory_id": DAY14_TERRITORY_IDS[city],
            "territory_name": city.replace('_', ' '),
            "url": f"https://queridodiario.ok.org.br/gazettes/{DAY14_TERRITORY_IDS[city]}-{date}",
            "excerpts": [excerpt],
            "edition_number": str(random.randint(1, 500)),
            "processed": True
        }

    def generate_city_data(self, city: str, since_date: str, until_date: str,
                          probability: float = 0.6) -> Dict:
        """
        Generate gazette data for a specific city.

        Args:
            city: City name
            since_date: Start date
            until_date: End date
            probability: Probability of city having publications (0.0-1.0)
        """
        # Not all cities publish every day
        if random.random() > probability:
            return {
                "total_gazettes": 0,
                "gazettes": []
            }

        # Realistic number of publications (1-5 per day)
        num_gazettes = random.randint(1, 5)

        gazettes = []
        for _ in range(num_gazettes):
            # Pick a random date in range
            date = until_date  # Simplified: use until_date

            gazette = self.generate_gazette(city, date)
            gazettes.append(gazette)

        return {
            "total_gazettes": num_gazettes,
            "gazettes": gazettes
        }

    def calculate_kpis_from_synthetic(self, data: Dict) -> Dict:
        """Calculate KPIs from synthetic data."""
        total_regulations = 0
        active_municipalities = 0
        compliance_mentions = 0
        safety_incidents = 0

        for city, city_data in data.items():
            total_regs = city_data.get('total_gazettes', 0)
            total_regulations += total_regs

            if total_regs > 0:
                active_municipalities += 1

            # Count mentions in excerpts
            for gazette in city_data.get('gazettes', []):
                for excerpt in gazette.get('excerpts', []):
                    text_lower = excerpt.lower()

                    # Compliance keywords
                    for keyword in ['prazo', 'cumprimento', 'fiscalização', 'obrigatoriedade']:
                        compliance_mentions += text_lower.count(keyword)

                    # Safety keywords
                    for keyword in ['acidente', 'segurança', 'infração', 'multa']:
                        safety_incidents += text_lower.count(keyword)

        return {
            'new_regulations': total_regulations,
            'active_municipalities': active_municipalities,
            'compliance_mentions': compliance_mentions,
            'safety_incidents': safety_incidents,
            'timestamp': datetime.now().isoformat(),
            'cities_monitored': len(data)
        }

    def generate_daily_report(self, days_back: int = 1) -> Dict:
        """
        Generate complete daily report with synthetic data.

        Args:
            days_back: Number of days to simulate

        Returns:
            Complete report structure matching real API format
        """
        until_date = datetime.now().strftime('%Y-%m-%d')
        since_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

        print(f"Generating synthetic data for {since_date} to {until_date}...")

        # Generate data for all cities
        transport_data = {}
        compliance_data = {}
        safety_data = {}

        for city in self.cities:
            print(f"  Generating data for {city}...")

            # Transport data (higher probability)
            transport_data[city] = self.generate_city_data(
                city, since_date, until_date, probability=0.5
            )

            # Compliance data (medium probability)
            compliance_data[city] = self.generate_city_data(
                city, since_date, until_date, probability=0.4
            )

            # Safety data (lower probability - not all cities report daily)
            safety_data[city] = self.generate_city_data(
                city, since_date, until_date, probability=0.3
            )

        # Calculate KPIs
        kpis = self.calculate_kpis_from_synthetic(transport_data)

        # Combine all counts
        kpis['compliance_mentions'] += self.calculate_kpis_from_synthetic(compliance_data)['new_regulations']
        kpis['safety_incidents'] += self.calculate_kpis_from_synthetic(safety_data)['new_regulations']

        return {
            'kpis': kpis,
            'date_range': {
                'since': since_date,
                'until': until_date
            },
            'raw_data': {
                'transport': transport_data,
                'compliance': compliance_data,
                'safety': safety_data
            },
            'metadata': {
                'data_source': 'synthetic',
                'reason': 'Querido Diário API blocked by Cloudflare (403 Forbidden)',
                'generated_at': datetime.now().isoformat(),
                'note': 'Synthetic data based on real API structure and realistic patterns'
            }
        }


def day14_generate_synthetic_report(days_back: int = 1, save_to_file: bool = True) -> Dict:
    """
    Main function to generate synthetic report.

    Args:
        days_back: Number of days to simulate
        save_to_file: Whether to save to JSON file

    Returns:
        Complete synthetic report
    """
    generator = Day14SyntheticDataGenerator()
    report = generator.generate_daily_report(days_back=days_back)

    if save_to_file:
        output_path = './data/day14_querido_diario_cache.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Synthetic report saved to {output_path}")

    return report


if __name__ == '__main__':
    """Generate and display synthetic report."""
    print("=" * 60)
    print("Day 14: Synthetic Transport Regulatory Data Generator")
    print("=" * 60)
    print()
    print("NOTE: Using synthetic data because Querido Diário API")
    print("is protected by Cloudflare and blocks automated requests.")
    print()
    print("This generates realistic data based on:")
    print("- Real API structure")
    print("- Actual Brazilian transport regulation patterns")
    print("- Realistic KPI distributions")
    print()
    print("=" * 60)
    print()

    # Generate report
    report = day14_generate_synthetic_report(days_back=1)

    # Display summary
    print("\n" + "=" * 60)
    print("KPI SUMMARY")
    print("=" * 60)
    print(json.dumps(report['kpis'], indent=2, ensure_ascii=False))

    print("\n" + "=" * 60)
    print("ACTIVE CITIES")
    print("=" * 60)
    active_cities = [
        city for city, data in report['raw_data']['transport'].items()
        if data['total_gazettes'] > 0
    ]
    for city in active_cities:
        count = report['raw_data']['transport'][city]['total_gazettes']
        print(f"  • {city.replace('_', ' ')}: {count} gazette(s)")

    print("\n✅ Data generation complete!")
    print(f"\nTo use in n8n workflow:")
    print(f"1. Start proxy: python3 day14_API_PROXY.py")
    print(f"2. Proxy will serve this synthetic data")
    print(f"3. n8n will process it normally")
