"""
Yoga Detector for Vedic Astrology
Detects planetary yogas (combinations) in a birth chart
"""

from typing import Dict, List, Tuple

class YogaDetector:
    """Detect various planetary yogas in a Vedic birth chart"""

    # Planet properties
    NATURAL_BENEFICS = ['Jupiter', 'Venus', 'Moon', 'Mercury']
    NATURAL_MALEFICS = ['Sun', 'Mars', 'Saturn', 'Rahu', 'Ketu']

    # Exaltation signs
    EXALTATION = {
        'Sun': 'Aries', 'Moon': 'Taurus', 'Mars': 'Capricorn',
        'Mercury': 'Virgo', 'Jupiter': 'Cancer', 'Venus': 'Pisces',
        'Saturn': 'Libra', 'Rahu': 'Taurus', 'Ketu': 'Scorpio'
    }

    # Debilitation signs (opposite to exaltation)
    DEBILITATION = {
        'Sun': 'Libra', 'Moon': 'Scorpio', 'Mars': 'Cancer',
        'Mercury': 'Pisces', 'Jupiter': 'Capricorn', 'Venus': 'Virgo',
        'Saturn': 'Aries', 'Rahu': 'Scorpio', 'Ketu': 'Taurus'
    }

    # Own signs
    OWN_SIGNS = {
        'Sun': ['Leo'],
        'Moon': ['Cancer'],
        'Mars': ['Aries', 'Scorpio'],
        'Mercury': ['Gemini', 'Virgo'],
        'Jupiter': ['Sagittarius', 'Pisces'],
        'Venus': ['Taurus', 'Libra'],
        'Saturn': ['Capricorn', 'Aquarius'],
        'Rahu': [],  # No own sign
        'Ketu': []   # No own sign
    }

    # Kendra houses (angular)
    KENDRA_HOUSES = [1, 4, 7, 10]

    # Trikona houses (trines)
    TRIKONA_HOUSES = [1, 5, 9]

    # Dusthana houses (malefic)
    DUSTHANA_HOUSES = [6, 8, 12]

    def __init__(self):
        """Initialize yoga detector"""
        self.yogas_found = []

    def get_planet_house(self, planet_data: Dict, houses: List[Dict]) -> int:
        """Determine which house a planet is in"""
        planet_sign_num = planet_data['sign_num']

        # In Vedic astrology (whole sign houses), house = sign offset from ascendant
        for house in houses:
            if house['sign_num'] == planet_sign_num:
                return house['house']

        return 1  # Default to first house

    def is_in_kendra(self, house: int) -> bool:
        """Check if planet is in a Kendra (angular house)"""
        return house in self.KENDRA_HOUSES

    def is_in_trikona(self, house: int) -> bool:
        """Check if planet is in a Trikona (trine house)"""
        return house in self.TRIKONA_HOUSES

    def is_in_dusthana(self, house: int) -> bool:
        """Check if planet is in a Dusthana (malefic house)"""
        return house in self.DUSTHANA_HOUSES

    def is_exalted(self, planet: str, sign: str) -> bool:
        """Check if planet is exalted"""
        return self.EXALTATION.get(planet) == sign

    def is_debilitated(self, planet: str, sign: str) -> bool:
        """Check if planet is debilitated"""
        return self.DEBILITATION.get(planet) == sign

    def is_in_own_sign(self, planet: str, sign: str) -> bool:
        """Check if planet is in its own sign"""
        return sign in self.OWN_SIGNS.get(planet, [])

    def planets_in_conjunction(self, planet1_data: Dict, planet2_data: Dict, orb: float = 10.0) -> bool:
        """Check if two planets are in conjunction (within orb)"""
        long1 = planet1_data['longitude']
        long2 = planet2_data['longitude']

        diff = abs(long1 - long2)
        # Account for zodiac wrap-around
        if diff > 180:
            diff = 360 - diff

        return diff <= orb

    def get_house_lord(self, house_num: int, houses: List[Dict], planets: Dict) -> str:
        """Get the planet that rules a house (simplified)"""
        # Find the sign of the house
        house_sign = None
        for h in houses:
            if h['house'] == house_num:
                house_sign = h['sign']
                break

        if not house_sign:
            return None

        # Find planet that rules this sign
        for planet, signs in self.OWN_SIGNS.items():
            if house_sign in signs:
                return planet

        return None

    def detect_raja_yoga(self, planets: Dict, houses: List[Dict]) -> List[Dict]:
        """
        Detect Raja Yogas (combinations for power and prosperity)
        Formed when Kendra lords and Trikona lords combine
        """
        yogas = []

        # Get lords of Kendras and Trikonas
        kendra_lords = []
        trikona_lords = []

        for house_num in self.KENDRA_HOUSES:
            lord = self.get_house_lord(house_num, houses, planets)
            if lord and lord not in ['Sun', 'Moon']:  # Exclude Sun and Moon for this
                kendra_lords.append((lord, house_num))

        for house_num in self.TRIKONA_HOUSES:
            lord = self.get_house_lord(house_num, houses, planets)
            if lord and lord not in ['Sun', 'Moon']:
                trikona_lords.append((lord, house_num))

        # Check for conjunctions between Kendra and Trikona lords
        for kendra_lord, kendra_house in kendra_lords:
            for trikona_lord, trikona_house in trikona_lords:
                if kendra_lord != trikona_lord:
                    if kendra_lord in planets and trikona_lord in planets:
                        if self.planets_in_conjunction(planets[kendra_lord], planets[trikona_lord]):
                            yogas.append({
                                'name': 'Raja Yoga',
                                'type': 'Prosperity',
                                'description': f'Lord of {kendra_house}th house ({kendra_lord}) conjunct with lord of {trikona_house}th house ({trikona_lord})',
                                'planets': [kendra_lord, trikona_lord],
                                'strength': 'Strong',
                                'effects': 'Power, authority, success, prosperity, recognition'
                            })

        return yogas

    def detect_dhana_yoga(self, planets: Dict, houses: List[Dict]) -> List[Dict]:
        """
        Detect Dhana Yogas (wealth combinations)
        Formed by connections between lords of 2, 5, 9, and 11
        """
        yogas = []

        wealth_houses = [2, 5, 9, 11]  # Houses of wealth
        wealth_lords = []

        for house_num in wealth_houses:
            lord = self.get_house_lord(house_num, houses, planets)
            if lord:
                wealth_lords.append((lord, house_num))

        # Check for conjunctions between wealth house lords
        for i, (lord1, house1) in enumerate(wealth_lords):
            for lord2, house2 in wealth_lords[i+1:]:
                if lord1 != lord2 and lord1 in planets and lord2 in planets:
                    if self.planets_in_conjunction(planets[lord1], planets[lord2]):
                        yogas.append({
                            'name': 'Dhana Yoga',
                            'type': 'Wealth',
                            'description': f'Lord of {house1}th house ({lord1}) conjunct with lord of {house2}th house ({lord2})',
                            'planets': [lord1, lord2],
                            'strength': 'Moderate',
                            'effects': 'Wealth accumulation, financial prosperity, material success'
                        })

        return yogas

    def detect_gajakesari_yoga(self, planets: Dict, houses: List[Dict]) -> List[Dict]:
        """
        Detect Gaja Kesari Yoga (Moon-Jupiter combination)
        Formed when Jupiter is in a Kendra from Moon
        """
        yogas = []

        if 'Jupiter' not in planets or 'Moon' not in planets:
            return yogas

        moon_house = self.get_planet_house(planets['Moon'], houses)
        jupiter_house = self.get_planet_house(planets['Jupiter'], houses)

        # Calculate house distance
        house_diff = (jupiter_house - moon_house) % 12
        if house_diff == 0:
            house_diff = 12

        # Kendra from Moon means houses 1, 4, 7, 10 from Moon
        if house_diff in [1, 4, 7, 10]:
            yogas.append({
                'name': 'Gaja Kesari Yoga',
                'type': 'Prosperity',
                'description': f'Jupiter in {house_diff}th house from Moon (Kendra position)',
                'planets': ['Jupiter', 'Moon'],
                'strength': 'Very Strong',
                'effects': 'Wisdom, wealth, good character, respect, leadership qualities, longevity'
            })

        return yogas

    def detect_pancha_mahapurusha_yogas(self, planets: Dict, houses: List[Dict]) -> List[Dict]:
        """
        Detect Pancha Mahapurusha Yogas (5 great yogas)
        Formed when Mars, Mercury, Jupiter, Venus, or Saturn are in own/exaltation sign in Kendra
        """
        yogas = []

        yoga_planets = {
            'Mars': {'name': 'Ruchaka Yoga', 'qualities': 'Courage, leadership, physical strength'},
            'Mercury': {'name': 'Bhadra Yoga', 'qualities': 'Intelligence, eloquence, learning'},
            'Jupiter': {'name': 'Hamsa Yoga', 'qualities': 'Wisdom, righteousness, spirituality'},
            'Venus': {'name': 'Malavya Yoga', 'qualities': 'Beauty, luxury, artistic talents'},
            'Saturn': {'name': 'Sasa Yoga', 'qualities': 'Authority, discipline, longevity'}
        }

        for planet, yoga_info in yoga_planets.items():
            if planet not in planets:
                continue

            planet_data = planets[planet]
            planet_sign = planet_data['sign']
            planet_house = self.get_planet_house(planet_data, houses)

            # Check if planet is in Kendra
            if not self.is_in_kendra(planet_house):
                continue

            # Check if planet is in own sign or exalted
            is_strong = self.is_in_own_sign(planet, planet_sign) or self.is_exalted(planet, planet_sign)

            if is_strong:
                yogas.append({
                    'name': yoga_info['name'],
                    'type': 'Mahapurusha',
                    'description': f'{planet} in {planet_sign} (own/exaltation) in {planet_house}th house (Kendra)',
                    'planets': [planet],
                    'strength': 'Very Strong',
                    'effects': yoga_info['qualities']
                })

        return yogas

    def detect_neecha_bhanga_raja_yoga(self, planets: Dict, houses: List[Dict]) -> List[Dict]:
        """
        Detect Neecha Bhanga Raja Yoga (cancellation of debilitation)
        Formed when a debilitated planet's debilitation is cancelled
        """
        yogas = []

        for planet, planet_data in planets.items():
            if planet in ['Rahu', 'Ketu', 'Ascendant']:
                continue

            planet_sign = planet_data['sign']

            # Check if planet is debilitated
            if not self.is_debilitated(planet, planet_sign):
                continue

            # Find the lord of debilitation sign
            debil_lord = None
            for lord, signs in self.OWN_SIGNS.items():
                if planet_sign in signs:
                    debil_lord = lord
                    break

            if not debil_lord or debil_lord not in planets:
                continue

            # Cancellation conditions:
            # 1. Lord of debilitation sign is in Kendra from Lagna or Moon
            debil_lord_house = self.get_planet_house(planets[debil_lord], houses)

            if self.is_in_kendra(debil_lord_house):
                yogas.append({
                    'name': 'Neecha Bhanga Raja Yoga',
                    'type': 'Cancellation',
                    'description': f'{planet} debilitated in {planet_sign}, but cancelled by {debil_lord} in Kendra',
                    'planets': [planet, debil_lord],
                    'strength': 'Strong',
                    'effects': 'Transformation of weakness into strength, unexpected rise, overcoming obstacles'
                })

        return yogas

    def detect_budhaditya_yoga(self, planets: Dict) -> List[Dict]:
        """
        Detect Budhaditya Yoga (Sun-Mercury conjunction)
        Gives intelligence and communication skills
        """
        yogas = []

        if 'Sun' in planets and 'Mercury' in planets:
            if self.planets_in_conjunction(planets['Sun'], planets['Mercury'], orb=15):
                # Budhaditya yoga, but check if not combust
                degree_diff = abs(planets['Sun']['longitude'] - planets['Mercury']['longitude'])

                status = 'Moderate'
                effects = 'Intelligence, learning, communication skills'

                if degree_diff < 3:
                    status = 'Weak (Combust)'
                    effects += ', but Mercury is combust (weakened)'

                yogas.append({
                    'name': 'Budhaditya Yoga',
                    'type': 'Intelligence',
                    'description': f'Sun and Mercury conjunction in {planets["Sun"]["sign"]}',
                    'planets': ['Sun', 'Mercury'],
                    'strength': status,
                    'effects': effects
                })

        return yogas

    def detect_chandra_mangala_yoga(self, planets: Dict) -> List[Dict]:
        """
        Detect Chandra Mangala Yoga (Moon-Mars conjunction)
        Gives wealth through mother or property
        """
        yogas = []

        if 'Moon' in planets and 'Mars' in planets:
            if self.planets_in_conjunction(planets['Moon'], planets['Mars']):
                yogas.append({
                    'name': 'Chandra Mangala Yoga',
                    'type': 'Wealth',
                    'description': f'Moon and Mars conjunction in {planets["Moon"]["sign"]}',
                    'planets': ['Moon', 'Mars'],
                    'strength': 'Moderate',
                    'effects': 'Wealth through property, mother, courage with emotions'
                })

        return yogas

    def detect_all_yogas(self, chart_data: Dict) -> Dict:
        """
        Detect all yogas in a birth chart

        Args:
            chart_data: Complete birth chart data from VedicCalculator

        Returns:
            Dictionary containing all detected yogas categorized by type
        """
        planets = chart_data['planets']
        houses = chart_data['houses']

        all_yogas = []

        # Detect various yogas
        all_yogas.extend(self.detect_raja_yoga(planets, houses))
        all_yogas.extend(self.detect_dhana_yoga(planets, houses))
        all_yogas.extend(self.detect_gajakesari_yoga(planets, houses))
        all_yogas.extend(self.detect_pancha_mahapurusha_yogas(planets, houses))
        all_yogas.extend(self.detect_neecha_bhanga_raja_yoga(planets, houses))
        all_yogas.extend(self.detect_budhaditya_yoga(planets))
        all_yogas.extend(self.detect_chandra_mangala_yoga(planets))

        # Categorize yogas
        categorized = {
            'prosperity': [],
            'wealth': [],
            'intelligence': [],
            'mahapurusha': [],
            'cancellation': [],
            'other': []
        }

        for yoga in all_yogas:
            yoga_type = yoga['type'].lower()
            if yoga_type == 'prosperity':
                categorized['prosperity'].append(yoga)
            elif yoga_type == 'wealth':
                categorized['wealth'].append(yoga)
            elif yoga_type == 'intelligence':
                categorized['intelligence'].append(yoga)
            elif yoga_type == 'mahapurusha':
                categorized['mahapurusha'].append(yoga)
            elif yoga_type == 'cancellation':
                categorized['cancellation'].append(yoga)
            else:
                categorized['other'].append(yoga)

        return {
            'total_yogas': len(all_yogas),
            'all_yogas': all_yogas,
            'by_category': categorized
        }

    def get_yoga_summary(self, yogas_data: Dict) -> str:
        """Generate a text summary of detected yogas"""
        summary = []
        summary.append(f"\n=== YOGAS DETECTED: {yogas_data['total_yogas']} ===\n")

        if yogas_data['total_yogas'] == 0:
            summary.append("No major yogas detected in this chart.")
            return "\n".join(summary)

        for yoga in yogas_data['all_yogas']:
            summary.append(f"{yoga['name']} ({yoga['type']})")
            summary.append(f"  Description: {yoga['description']}")
            summary.append(f"  Strength: {yoga['strength']}")
            summary.append(f"  Effects: {yoga['effects']}\n")

        return "\n".join(summary)
