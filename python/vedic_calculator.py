"""
Vedic Astrology Calculator
Calculates planetary positions, houses, nakshatras, and dashas using Swiss Ephemeris
"""

import swisseph as swe
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Tuple
import json

class VedicCalculator:
    """Calculate Vedic astrology chart data"""

    # Ayanamsa for Vedic calculations (Lahiri)
    AYANAMSA = swe.SIDM_LAHIRI

    # Planet IDs
    PLANETS = {
        'Sun': swe.SUN,
        'Moon': swe.MOON,
        'Mars': swe.MARS,
        'Mercury': swe.MERCURY,
        'Jupiter': swe.JUPITER,
        'Venus': swe.VENUS,
        'Saturn': swe.SATURN,
        'Rahu': swe.MEAN_NODE,  # North Node
        'Ketu': -1,  # South Node (180° from Rahu)
        'Ascendant': -2  # Special case
    }

    # Zodiac signs
    SIGNS = [
        'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
        'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
    ]

    # Nakshatras (27 lunar mansions)
    NAKSHATRAS = [
        'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
        'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
        'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
        'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha',
        'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
    ]

    # Nakshatra lords (Vimshottari Dasha sequence)
    NAKSHATRA_LORDS = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']

    def __init__(self):
        """Initialize calculator with Swiss Ephemeris settings"""
        swe.set_sid_mode(self.AYANAMSA)

    def calculate_julian_day(self, dt: datetime) -> float:
        """Convert datetime to Julian Day"""
        return swe.julday(dt.year, dt.month, dt.day,
                         dt.hour + dt.minute/60.0 + dt.second/3600.0)

    def get_ayanamsa(self, jd: float) -> float:
        """Get ayanamsa value for given Julian Day"""
        return swe.get_ayanamsa(jd)

    def calculate_planet_position(self, planet_id: int, jd: float, tropical: bool = False) -> Dict:
        """Calculate position of a planet"""
        if tropical:
            position = swe.calc_ut(jd, planet_id)[0]
        else:
            position = swe.calc_ut(jd, planet_id, swe.FLG_SIDEREAL)[0]

        longitude = position[0]
        sign_num = int(longitude / 30)
        degree_in_sign = longitude % 30

        return {
            'longitude': longitude,
            'sign': self.SIGNS[sign_num],
            'sign_num': sign_num + 1,
            'degree': degree_in_sign,
            'degree_formatted': f"{int(degree_in_sign)}°{int((degree_in_sign % 1) * 60)}'"
        }

    def calculate_ascendant(self, jd: float, latitude: float, longitude: float) -> Dict:
        """Calculate Ascendant (Lagna)"""
        # Calculate houses using Placidus system
        cusps, ascmc = swe.houses(jd, latitude, longitude, b'P')

        # Get tropical ascendant
        tropical_asc = ascmc[0]

        # Convert to sidereal
        ayanamsa = self.get_ayanamsa(jd)
        sidereal_asc = (tropical_asc - ayanamsa) % 360

        sign_num = int(sidereal_asc / 30)
        degree_in_sign = sidereal_asc % 30

        return {
            'longitude': sidereal_asc,
            'sign': self.SIGNS[sign_num],
            'sign_num': sign_num + 1,
            'degree': degree_in_sign,
            'degree_formatted': f"{int(degree_in_sign)}°{int((degree_in_sign % 1) * 60)}'"
        }

    def calculate_houses(self, jd: float, latitude: float, longitude: float) -> List[Dict]:
        """Calculate 12 houses using Whole Sign system (Vedic)"""
        ascendant = self.calculate_ascendant(jd, latitude, longitude)
        asc_sign = ascendant['sign_num'] - 1  # 0-indexed

        houses = []
        for i in range(12):
            house_sign = (asc_sign + i) % 12
            houses.append({
                'house': i + 1,
                'sign': self.SIGNS[house_sign],
                'sign_num': house_sign + 1,
                'degree_start': house_sign * 30,
                'degree_end': (house_sign + 1) * 30
            })

        return houses

    def calculate_nakshatra(self, longitude: float) -> Dict:
        """Calculate Nakshatra for a given longitude"""
        nakshatra_length = 360 / 27  # 13.333... degrees
        nakshatra_num = int(longitude / nakshatra_length)
        pada = int((longitude % nakshatra_length) / (nakshatra_length / 4)) + 1
        lord_index = nakshatra_num % 9

        return {
            'nakshatra': self.NAKSHATRAS[nakshatra_num],
            'nakshatra_num': nakshatra_num + 1,
            'pada': pada,
            'lord': self.NAKSHATRA_LORDS[lord_index]
        }

    def calculate_chart(self, birth_datetime: datetime, latitude: float, longitude: float) -> Dict:
        """Calculate complete Vedic birth chart"""
        jd = self.calculate_julian_day(birth_datetime)

        # Calculate Ascendant
        ascendant_data = self.calculate_ascendant(jd, latitude, longitude)

        # Calculate planetary positions
        planets = {}
        for planet_name, planet_id in self.PLANETS.items():
            if planet_name == 'Ascendant':
                planets['Ascendant'] = ascendant_data
                planets['Ascendant']['nakshatra'] = self.calculate_nakshatra(ascendant_data['longitude'])
            elif planet_name == 'Ketu':
                # Ketu is 180° opposite to Rahu
                rahu_pos = planets['Rahu']['longitude']
                ketu_long = (rahu_pos + 180) % 360
                sign_num = int(ketu_long / 30)
                degree_in_sign = ketu_long % 30

                planets['Ketu'] = {
                    'longitude': ketu_long,
                    'sign': self.SIGNS[sign_num],
                    'sign_num': sign_num + 1,
                    'degree': degree_in_sign,
                    'degree_formatted': f"{int(degree_in_sign)}°{int((degree_in_sign % 1) * 60)}'",
                    'nakshatra': self.calculate_nakshatra(ketu_long)
                }
            else:
                planet_data = self.calculate_planet_position(planet_id, jd)
                planet_data['nakshatra'] = self.calculate_nakshatra(planet_data['longitude'])
                planets[planet_name] = planet_data

        # Calculate houses
        houses = self.calculate_houses(jd, latitude, longitude)

        # Calculate Vimshottari Dasha
        moon_nakshatra = planets['Moon']['nakshatra']
        dasha_info = self.calculate_vimshottari_dasha(birth_datetime, moon_nakshatra)

        return {
            'birth_datetime': birth_datetime.isoformat(),
            'location': {'latitude': latitude, 'longitude': longitude},
            'ayanamsa': self.get_ayanamsa(jd),
            'planets': planets,
            'houses': houses,
            'dasha': dasha_info
        }

    def calculate_vimshottari_dasha(self, birth_datetime: datetime, moon_nakshatra: Dict) -> Dict:
        """Calculate Vimshottari Dasha periods"""
        # Dasha years for each planet
        dasha_years = {
            'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10,
            'Mars': 7, 'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
        }

        # Starting planet based on Moon's nakshatra
        starting_lord = moon_nakshatra['lord']

        # Calculate balance of first dasha based on Moon's position in nakshatra
        # This is simplified - actual calculation is more complex
        nakshatra_length = 360 / 27
        moon_long = moon_nakshatra['nakshatra_num'] * nakshatra_length

        current_date = birth_datetime
        dashas = []

        # Get starting index
        start_idx = self.NAKSHATRA_LORDS.index(starting_lord)

        # Calculate major dasha periods
        for i in range(9):
            lord_idx = (start_idx + i) % 9
            lord = self.NAKSHATRA_LORDS[lord_idx]
            years = dasha_years[lord]

            end_date = current_date + timedelta(days=years * 365.25)

            dashas.append({
                'lord': lord,
                'start': current_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d'),
                'years': years
            })

            current_date = end_date

        # Determine current dasha
        now = datetime.now(pytz.UTC)
        if birth_datetime.tzinfo is None:
            now = now.replace(tzinfo=None)

        current_dasha = None
        for dasha in dashas:
            start = datetime.fromisoformat(dasha['start'])
            end = datetime.fromisoformat(dasha['end'])
            if start <= now <= end:
                current_dasha = dasha
                break

        return {
            'system': 'Vimshottari',
            'periods': dashas,
            'current_mahadasha': current_dasha
        }

    def get_chart_summary(self, chart_data: Dict) -> str:
        """Generate a text summary of the chart"""
        planets = chart_data['planets']
        houses = chart_data['houses']
        dasha = chart_data['dasha']

        summary = []
        summary.append("=== VEDIC BIRTH CHART ===\n")
        summary.append(f"Birth Date: {chart_data['birth_datetime']}")
        summary.append(f"Ayanamsa: {chart_data['ayanamsa']:.2f}°\n")

        summary.append("ASCENDANT (Lagna):")
        asc = planets['Ascendant']
        summary.append(f"  {asc['sign']} {asc['degree_formatted']} - {asc['nakshatra']['nakshatra']} (Pada {asc['nakshatra']['pada']})\n")

        summary.append("PLANETARY POSITIONS:")
        for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']:
            p = planets[planet]
            summary.append(f"  {planet:8} - {p['sign']:12} {p['degree_formatted']:8} - {p['nakshatra']['nakshatra']} (Pada {p['nakshatra']['pada']})")

        if dasha['current_mahadasha']:
            summary.append(f"\nCURRENT MAHADASHA: {dasha['current_mahadasha']['lord']} ({dasha['current_mahadasha']['start']} to {dasha['current_mahadasha']['end']})")

        return "\n".join(summary)
