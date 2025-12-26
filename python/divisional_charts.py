"""
Divisional Charts (Varga Charts) Calculator
Calculates various divisional charts used in Vedic Astrology
"""

from typing import Dict, List
from vedic_calculator import VedicCalculator

class DivisionalCharts:
    """Calculate divisional charts (Vargas) for detailed analysis"""

    SIGNS = VedicCalculator.SIGNS

    # Divisional chart information
    CHART_INFO = {
        'D1': {'name': 'Rasi', 'divisions': 1, 'signification': 'Physical body, overall life'},
        'D2': {'name': 'Hora', 'divisions': 2, 'signification': 'Wealth,财富'},
        'D3': {'name': 'Drekkana', 'divisions': 3, 'signification': 'Siblings, courage'},
        'D4': {'name': 'Chaturthamsa', 'divisions': 4, 'signification': 'Fortune, property'},
        'D7': {'name': 'Saptamsa', 'divisions': 7, 'signification': 'Children, progeny'},
        'D9': {'name': 'Navamsa', 'divisions': 9, 'signification': 'Spouse, dharma, fortune'},
        'D10': {'name': 'Dasamsa', 'divisions': 10, 'signification': 'Career, profession'},
        'D12': {'name': 'Dwadasamsa', 'divisions': 12, 'signification': 'Parents'},
        'D16': {'name': 'Shodasamsa', 'divisions': 16, 'signification': 'Vehicles, luxuries'},
        'D20': {'name': 'Vimsamsa', 'divisions': 20, 'signification': 'Spiritual practices'},
        'D24': {'name': 'Chaturvimsamsa', 'divisions': 24, 'signification': 'Education, learning'},
        'D27': {'name': 'Bhamsa', 'divisions': 27, 'signification': 'Strengths, weaknesses'},
        'D30': {'name': 'Trimsamsa', 'divisions': 30, 'signification': 'Misfortunes, evils'},
        'D40': {'name': 'Khavedamsa', 'divisions': 40, 'signification': 'Auspicious/inauspicious effects'},
        'D45': {'name': 'Akshavedamsa', 'divisions': 45, 'signification': 'General character'},
        'D60': {'name': 'Shashtiamsa', 'divisions': 60, 'signification': 'Past life karma'},
    }

    def __init__(self):
        """Initialize divisional chart calculator"""
        pass

    def calculate_d9_navamsa(self, longitude: float) -> Dict:
        """
        Calculate D9 (Navamsa) position - most important divisional chart
        Each sign is divided into 9 parts of 3°20' each
        """
        sign = int(longitude / 30)
        degree_in_sign = longitude % 30

        # Each navamsa is 3°20' (3.333...)
        navamsa_in_sign = int(degree_in_sign / (30/9))

        # Navamsa chart follows a specific pattern based on sign type
        # Movable signs (Aries, Cancer, Libra, Capricorn): start from same sign
        # Fixed signs (Taurus, Leo, Scorpio, Aquarius): start from 9th sign
        # Dual signs (Gemini, Virgo, Sagittarius, Pisces): start from 5th sign

        sign_type = sign % 3
        if sign_type == 0:  # Movable (Chara)
            navamsa_sign = (sign + navamsa_in_sign) % 12
        elif sign_type == 1:  # Fixed (Sthira)
            navamsa_sign = (sign + 8 + navamsa_in_sign) % 12
        else:  # Dual (Dvisvabhava)
            navamsa_sign = (sign + 4 + navamsa_in_sign) % 12

        # Calculate degree within navamsa sign
        degree_within_navamsa = (degree_in_sign % (30/9)) * 9

        return {
            'sign': self.SIGNS[navamsa_sign],
            'sign_num': navamsa_sign + 1,
            'degree': degree_within_navamsa,
            'degree_formatted': f"{int(degree_within_navamsa)}°{int((degree_within_navamsa % 1) * 60)}'"
        }

    def calculate_d10_dasamsa(self, longitude: float) -> Dict:
        """
        Calculate D10 (Dasamsa) position - career chart
        Each sign is divided into 10 parts of 3° each
        """
        sign = int(longitude / 30)
        degree_in_sign = longitude % 30

        # Each dasamsa is 3°
        dasamsa_in_sign = int(degree_in_sign / 3)

        # Odd signs: count from same sign
        # Even signs: count from 9th sign
        if sign % 2 == 0:  # Odd sign (1st, 3rd, 5th... are index 0, 2, 4...)
            dasamsa_sign = (sign + dasamsa_in_sign) % 12
        else:  # Even sign
            dasamsa_sign = (sign + 8 + dasamsa_in_sign) % 12

        degree_within_dasamsa = (degree_in_sign % 3) * 10

        return {
            'sign': self.SIGNS[dasamsa_sign],
            'sign_num': dasamsa_sign + 1,
            'degree': degree_within_dasamsa,
            'degree_formatted': f"{int(degree_within_dasamsa)}°{int((degree_within_dasamsa % 1) * 60)}'"
        }

    def calculate_d7_saptamsa(self, longitude: float) -> Dict:
        """
        Calculate D7 (Saptamsa) position - children chart
        Each sign is divided into 7 parts
        """
        sign = int(longitude / 30)
        degree_in_sign = longitude % 30

        # Each saptamsa is 30/7 = 4.2857°
        saptamsa_in_sign = int(degree_in_sign / (30/7))

        # Odd signs: count from same sign
        # Even signs: count from 7th sign
        if sign % 2 == 0:  # Odd sign
            saptamsa_sign = (sign + saptamsa_in_sign) % 12
        else:  # Even sign
            saptamsa_sign = (sign + 6 + saptamsa_in_sign) % 12

        degree_within_saptamsa = (degree_in_sign % (30/7)) * 7

        return {
            'sign': self.SIGNS[saptamsa_sign],
            'sign_num': saptamsa_sign + 1,
            'degree': degree_within_saptamsa,
            'degree_formatted': f"{int(degree_within_saptamsa)}°{int((degree_within_saptamsa % 1) * 60)}'"
        }

    def calculate_d12_dwadasamsa(self, longitude: float) -> Dict:
        """
        Calculate D12 (Dwadasamsa) position - parents chart
        Each sign is divided into 12 parts of 2°30' each
        """
        sign = int(longitude / 30)
        degree_in_sign = longitude % 30

        # Each dwadasamsa is 2.5°
        dwadasamsa_in_sign = int(degree_in_sign / 2.5)

        # All signs: count from same sign
        dwadasamsa_sign = (sign + dwadasamsa_in_sign) % 12

        degree_within_dwadasamsa = (degree_in_sign % 2.5) * 12

        return {
            'sign': self.SIGNS[dwadasamsa_sign],
            'sign_num': dwadasamsa_sign + 1,
            'degree': degree_within_dwadasamsa,
            'degree_formatted': f"{int(degree_within_dwadasamsa)}°{int((degree_within_dwadasamsa % 1) * 60)}'"
        }

    def calculate_d16_shodasamsa(self, longitude: float) -> Dict:
        """
        Calculate D16 (Shodasamsa) position - vehicles/luxuries chart
        Each sign is divided into 16 parts
        """
        sign = int(longitude / 30)
        degree_in_sign = longitude % 30

        # Each shodasamsa is 1.875°
        shodasamsa_in_sign = int(degree_in_sign / 1.875)

        # Movable signs: start from same sign
        # Fixed signs: start from 5th sign
        # Dual signs: start from 9th sign
        sign_type = sign % 3
        if sign_type == 0:  # Movable
            shodasamsa_sign = (sign + shodasamsa_in_sign) % 12
        elif sign_type == 1:  # Fixed
            shodasamsa_sign = (sign + 4 + shodasamsa_in_sign) % 12
        else:  # Dual
            shodasamsa_sign = (sign + 8 + shodasamsa_in_sign) % 12

        degree_within_shodasamsa = (degree_in_sign % 1.875) * 16

        return {
            'sign': self.SIGNS[shodasamsa_sign],
            'sign_num': shodasamsa_sign + 1,
            'degree': degree_within_shodasamsa,
            'degree_formatted': f"{int(degree_within_shodasamsa)}°{int((degree_within_shodasamsa % 1) * 60)}'"
        }

    def calculate_d20_vimsamsa(self, longitude: float) -> Dict:
        """
        Calculate D20 (Vimsamsa) position - spiritual chart
        Each sign is divided into 20 parts of 1°30' each
        """
        sign = int(longitude / 30)
        degree_in_sign = longitude % 30

        # Each vimsamsa is 1.5°
        vimsamsa_in_sign = int(degree_in_sign / 1.5)

        # Movable signs: start from same sign (Aries)
        # Fixed signs: start from 9th sign (Sagittarius)
        # Dual signs: start from 5th sign (Leo)
        sign_type = sign % 3
        if sign_type == 0:  # Movable
            vimsamsa_sign = (0 + vimsamsa_in_sign) % 12  # Start from Aries
        elif sign_type == 1:  # Fixed
            vimsamsa_sign = (8 + vimsamsa_in_sign) % 12  # Start from Sagittarius
        else:  # Dual
            vimsamsa_sign = (4 + vimsamsa_in_sign) % 12  # Start from Leo

        degree_within_vimsamsa = (degree_in_sign % 1.5) * 20

        return {
            'sign': self.SIGNS[vimsamsa_sign],
            'sign_num': vimsamsa_sign + 1,
            'degree': degree_within_vimsamsa,
            'degree_formatted': f"{int(degree_within_vimsamsa)}°{int((degree_within_vimsamsa % 1) * 60)}'"
        }

    def calculate_d24_chaturvimsamsa(self, longitude: float) -> Dict:
        """
        Calculate D24 (Chaturvimsamsa) position - education chart
        Each sign is divided into 24 parts of 1°15' each
        """
        sign = int(longitude / 30)
        degree_in_sign = longitude % 30

        # Each chaturvimsamsa is 1.25°
        chaturvimsamsa_in_sign = int(degree_in_sign / 1.25)

        # Odd signs: start from Leo (5th sign)
        # Even signs: start from Cancer (4th sign)
        if sign % 2 == 0:  # Odd sign
            chaturvimsamsa_sign = (4 + chaturvimsamsa_in_sign) % 12  # Start from Leo
        else:  # Even sign
            chaturvimsamsa_sign = (3 + chaturvimsamsa_in_sign) % 12  # Start from Cancer

        degree_within_chaturvimsamsa = (degree_in_sign % 1.25) * 24

        return {
            'sign': self.SIGNS[chaturvimsamsa_sign],
            'sign_num': chaturvimsamsa_sign + 1,
            'degree': degree_within_chaturvimsamsa,
            'degree_formatted': f"{int(degree_within_chaturvimsamsa)}°{int((degree_within_chaturvimsamsa % 1) * 60)}'"
        }

    def calculate_d30_trimsamsa(self, longitude: float) -> Dict:
        """
        Calculate D30 (Trimsamsa) position - misfortunes chart
        Each sign is divided into 30 parts of 1° each (special division pattern)
        """
        sign = int(longitude / 30)
        degree_in_sign = longitude % 30

        # Trimsamsa has a special pattern
        # Odd signs: Mars(5°), Saturn(5°), Jupiter(8°), Mercury(7°), Venus(5°)
        # Even signs: Venus(5°), Mercury(7°), Jupiter(8°), Saturn(5°), Mars(5°)

        if sign % 2 == 0:  # Odd signs
            if degree_in_sign < 5:
                trimsamsa_sign = (sign + 0) % 12  # Mars - same sign
            elif degree_in_sign < 10:
                trimsamsa_sign = (sign + 6) % 12  # Saturn - 7th sign
            elif degree_in_sign < 18:
                trimsamsa_sign = (sign + 8) % 12  # Jupiter - 9th sign
            elif degree_in_sign < 25:
                trimsamsa_sign = (sign + 2) % 12  # Mercury - 3rd sign
            else:
                trimsamsa_sign = (sign + 4) % 12  # Venus - 5th sign
        else:  # Even signs
            if degree_in_sign < 5:
                trimsamsa_sign = (sign + 4) % 12  # Venus
            elif degree_in_sign < 12:
                trimsamsa_sign = (sign + 2) % 12  # Mercury
            elif degree_in_sign < 20:
                trimsamsa_sign = (sign + 8) % 12  # Jupiter
            elif degree_in_sign < 25:
                trimsamsa_sign = (sign + 6) % 12  # Saturn
            else:
                trimsamsa_sign = (sign + 0) % 12  # Mars

        degree_within_trimsamsa = (degree_in_sign % 1) * 30

        return {
            'sign': self.SIGNS[trimsamsa_sign],
            'sign_num': trimsamsa_sign + 1,
            'degree': degree_within_trimsamsa,
            'degree_formatted': f"{int(degree_within_trimsamsa)}°{int((degree_within_trimsamsa % 1) * 60)}'"
        }

    def calculate_d60_shashtiamsa(self, longitude: float) -> Dict:
        """
        Calculate D60 (Shashtiamsa) position - past life karma
        Each sign is divided into 60 parts of 30' each
        """
        sign = int(longitude / 30)
        degree_in_sign = longitude % 30

        # Each shashtiamsa is 0.5°
        shashtiamsa_in_sign = int(degree_in_sign / 0.5)

        # All signs: count from same sign
        shashtiamsa_sign = (sign + shashtiamsa_in_sign) % 12

        degree_within_shashtiamsa = (degree_in_sign % 0.5) * 60

        return {
            'sign': self.SIGNS[shashtiamsa_sign],
            'sign_num': shashtiamsa_sign + 1,
            'degree': degree_within_shashtiamsa,
            'degree_formatted': f"{int(degree_within_shashtiamsa)}°{int((degree_within_shashtiamsa % 1) * 60)}'"
        }

    def calculate_divisional_chart(self, chart_type: str, planet_positions: Dict) -> Dict:
        """
        Calculate divisional chart for all planets

        Args:
            chart_type: Type of chart (D1, D9, D10, etc.)
            planet_positions: Dictionary of planet longitudes from main chart

        Returns:
            Dictionary with divisional positions for all planets
        """
        method_map = {
            'D1': lambda x: {'sign': self.SIGNS[int(x/30)], 'sign_num': int(x/30)+1,
                            'degree': x%30, 'degree_formatted': f"{int(x%30)}°{int(((x%30)%1)*60)}'"},
            'D7': self.calculate_d7_saptamsa,
            'D9': self.calculate_d9_navamsa,
            'D10': self.calculate_d10_dasamsa,
            'D12': self.calculate_d12_dwadasamsa,
            'D16': self.calculate_d16_shodasamsa,
            'D20': self.calculate_d20_vimsamsa,
            'D24': self.calculate_d24_chaturvimsamsa,
            'D30': self.calculate_d30_trimsamsa,
            'D60': self.calculate_d60_shashtiamsa,
        }

        if chart_type not in method_map:
            raise ValueError(f"Unsupported chart type: {chart_type}")

        calculation_method = method_map[chart_type]
        divisional_positions = {}

        for planet, data in planet_positions.items():
            longitude = data['longitude']
            divisional_positions[planet] = calculation_method(longitude)

        return {
            'chart_type': chart_type,
            'name': self.CHART_INFO.get(chart_type, {}).get('name', chart_type),
            'signification': self.CHART_INFO.get(chart_type, {}).get('signification', ''),
            'positions': divisional_positions
        }

    def get_all_divisional_charts(self, planet_positions: Dict, chart_types: List[str] = None) -> Dict:
        """
        Calculate multiple divisional charts

        Args:
            planet_positions: Planet positions from main chart
            chart_types: List of chart types to calculate (default: D9, D10, D12)

        Returns:
            Dictionary of all requested divisional charts
        """
        if chart_types is None:
            chart_types = ['D9', 'D10', 'D12']  # Most important ones

        charts = {}
        for chart_type in chart_types:
            charts[chart_type] = self.calculate_divisional_chart(chart_type, planet_positions)

        return charts
