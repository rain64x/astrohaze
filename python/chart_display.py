"""
Chart Display for Terminal
Beautiful visualization of Vedic astrology charts using Rich library
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich import box
from typing import Dict, List


class ChartDisplay:
    """Display Vedic astrology charts in terminal with Rich formatting"""

    def __init__(self):
        """Initialize chart display"""
        self.console = Console()

    def display_planets_table(self, planets: Dict) -> Table:
        """Create a table showing planetary positions"""
        table = Table(title="Planetary Positions", box=box.ROUNDED, title_style="bold cyan")

        table.add_column("Planet", style="yellow", justify="left")
        table.add_column("Sign", style="green")
        table.add_column("Degree", style="white")
        table.add_column("Nakshatra", style="magenta")
        table.add_column("Pada", style="cyan")

        # Order of planets to display
        planet_order = ['Ascendant', 'Sun', 'Moon', 'Mars', 'Mercury',
                       'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']

        for planet in planet_order:
            if planet in planets:
                p = planets[planet]
                table.add_row(
                    planet,
                    p['sign'],
                    p['degree_formatted'],
                    p['nakshatra']['nakshatra'],
                    str(p['nakshatra']['pada'])
                )

        return table

    def display_houses_table(self, houses: List[Dict]) -> Table:
        """Create a table showing house cusps"""
        table = Table(title="House Cusps (Whole Sign System)", box=box.ROUNDED, title_style="bold cyan")

        table.add_column("House", style="yellow", justify="center")
        table.add_column("Sign", style="green")
        table.add_column("Sign Number", style="white")

        for house in houses:
            table.add_row(
                str(house['house']),
                house['sign'],
                str(house['sign_num'])
            )

        return table

    def display_dasha_periods(self, dasha: Dict) -> Table:
        """Create a table showing Vimshottari Dasha periods"""
        table = Table(title="Vimshottari Mahadasha Periods", box=box.ROUNDED, title_style="bold cyan")

        table.add_column("Lord", style="yellow")
        table.add_column("Start Date", style="green")
        table.add_column("End Date", style="green")
        table.add_column("Years", style="white")
        table.add_column("Status", style="cyan")

        current_dasha = dasha.get('current_mahadasha')

        for period in dasha.get('periods', []):
            status = ""
            style = ""

            if current_dasha and period['lord'] == current_dasha['lord']:
                status = "CURRENT"
                style = "bold red"
            else:
                style = "dim"

            table.add_row(
                period['lord'],
                period['start'],
                period['end'],
                str(period['years']),
                status,
                style=style
            )

        return table

    def display_yogas_panel(self, yogas_data: Dict) -> Panel:
        """Create a panel showing detected yogas"""
        if yogas_data['total_yogas'] == 0:
            return Panel(
                "[yellow]No major yogas detected in this chart.[/yellow]",
                title="Planetary Yogas",
                border_style="cyan"
            )

        yoga_text = []
        for yoga in yogas_data['all_yogas']:
            yoga_text.append(f"[bold yellow]{yoga['name']}[/bold yellow] ({yoga['type']})")
            yoga_text.append(f"  [dim]{yoga['description']}[/dim]")
            yoga_text.append(f"  [green]Strength:[/green] {yoga['strength']}")
            yoga_text.append(f"  [cyan]Effects:[/cyan] {yoga['effects']}")
            yoga_text.append("")

        content = "\n".join(yoga_text)

        return Panel(
            content,
            title=f"Planetary Yogas ({yogas_data['total_yogas']} found)",
            border_style="cyan",
            box=box.ROUNDED
        )

    def display_divisional_chart(self, div_chart: Dict) -> Table:
        """Display a divisional chart"""
        table = Table(
            title=f"{div_chart['chart_type']} - {div_chart['name']}",
            caption=f"Signification: {div_chart['signification']}",
            box=box.ROUNDED,
            title_style="bold cyan"
        )

        table.add_column("Planet", style="yellow")
        table.add_column("Sign", style="green")
        table.add_column("Degree", style="white")

        for planet, pos in div_chart['positions'].items():
            if planet != 'Ascendant':
                table.add_row(
                    planet,
                    pos['sign'],
                    pos.get('degree_formatted', '')
                )

        return table

    def display_chart_header(self, chart_data: Dict) -> Panel:
        """Display chart header with birth details"""
        birth_dt = chart_data.get('birth_datetime', 'Unknown')
        location = chart_data.get('location', {})
        ayanamsa = chart_data.get('ayanamsa', 0)

        content = f"""[bold cyan]Birth Date:[/bold cyan] {birth_dt}
[bold cyan]Location:[/bold cyan] Lat {location.get('latitude', 'N/A')}°, Lon {location.get('longitude', 'N/A')}°
[bold cyan]Ayanamsa:[/bold cyan] {ayanamsa:.2f}° (Lahiri)
[bold cyan]System:[/bold cyan] Vedic (Sidereal Zodiac, Whole Sign Houses)"""

        return Panel(
            content,
            title="Birth Chart Details",
            border_style="green",
            box=box.DOUBLE
        )

    def display_ascii_chart(self, planets: Dict, houses: List[Dict]) -> str:
        """
        Display a simplified ASCII chart showing planets in houses
        This is a simple North Indian style chart representation
        """
        # Create a 4x4 grid representing the 12 houses
        # North Indian chart layout:
        #  [12] [1] [2] [3]
        #  [11]         [4]
        #  [10]         [5]
        #  [9]  [8] [7] [6]

        # Initialize house contents
        house_contents = {i: [] for i in range(1, 13)}

        # Place planets in houses
        for planet, data in planets.items():
            if planet == 'Ascendant':
                continue  # Ascendant defines 1st house, already shown

            planet_sign_num = data['sign_num']

            # Find which house this planet is in
            for house in houses:
                if house['sign_num'] == planet_sign_num:
                    house_num = house['house']
                    # Use abbreviated planet names
                    abbrev = {
                        'Sun': 'Su', 'Moon': 'Mo', 'Mars': 'Ma',
                        'Mercury': 'Me', 'Jupiter': 'Ju', 'Venus': 'Ve',
                        'Saturn': 'Sa', 'Rahu': 'Ra', 'Ketu': 'Ke'
                    }
                    house_contents[house_num].append(abbrev.get(planet, planet[:2]))
                    break

        # Build the chart
        def format_house(house_num):
            planets_in_house = house_contents[house_num]
            planet_str = ','.join(planets_in_house) if planets_in_house else ''
            # Pad to consistent width
            return f"{house_num:2d}:{planet_str:8s}"

        chart = f"""
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ {format_house(12)} │ {format_house(1)} │ {format_house(2)} │ {format_house(3)} │
├─────────────┴─────────────┴─────────────┴─────────────┤
│ {format_house(11)}                                    {format_house(4)} │
│                                                         │
│ {format_house(10)}                                    {format_house(5)} │
├─────────────┬─────────────┬─────────────┬─────────────┤
│ {format_house(9)} │ {format_house(8)} │ {format_house(7)} │ {format_house(6)} │
└─────────────┴─────────────┴─────────────┴─────────────┘

Planet Abbreviations:
Su=Sun, Mo=Moon, Ma=Mars, Me=Mercury, Ju=Jupiter, Ve=Venus, Sa=Saturn, Ra=Rahu, Ke=Ketu
"""
        return chart

    def display_full_chart(self, chart_data: Dict, yogas_data: Dict = None):
        """Display complete chart with all information"""
        self.console.print("\n")
        self.console.print(self.display_chart_header(chart_data))
        self.console.print("\n")

        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(name="upper"),
            Layout(name="lower")
        )

        # ASCII chart
        ascii_chart = self.display_ascii_chart(chart_data['planets'], chart_data['houses'])
        self.console.print(Panel(ascii_chart, title="Birth Chart (North Indian Style)", border_style="yellow"))
        self.console.print("\n")

        # Planets table
        self.console.print(self.display_planets_table(chart_data['planets']))
        self.console.print("\n")

        # Houses table
        # self.console.print(self.display_houses_table(chart_data['houses']))
        # self.console.print("\n")

        # Dasha periods
        if 'dasha' in chart_data:
            self.console.print(self.display_dasha_periods(chart_data['dasha']))
            self.console.print("\n")

        # Yogas
        if yogas_data:
            self.console.print(self.display_yogas_panel(yogas_data))
            self.console.print("\n")

    def display_interpretation(self, title: str, interpretation: str):
        """Display AI interpretation in a formatted panel"""
        panel = Panel(
            interpretation,
            title=title,
            border_style="green",
            box=box.ROUNDED,
            padding=(1, 2)
        )
        self.console.print("\n")
        self.console.print(panel)
        self.console.print("\n")

    def display_menu(self, title: str, options: List[str]) -> None:
        """Display a menu with options"""
        table = Table(title=title, box=box.SIMPLE, show_header=False, title_style="bold cyan")
        table.add_column("Option", style="yellow", justify="right")
        table.add_column("Description", style="white")

        for i, option in enumerate(options, 1):
            table.add_row(str(i), option)

        table.add_row("0", "[red]Exit[/red]")

        self.console.print("\n")
        self.console.print(table)
        self.console.print("\n")

    def print_success(self, message: str):
        """Print success message"""
        self.console.print(f"[bold green]✓[/bold green] {message}")

    def print_error(self, message: str):
        """Print error message"""
        self.console.print(f"[bold red]✗[/bold red] {message}")

    def print_info(self, message: str):
        """Print info message"""
        self.console.print(f"[cyan]ℹ[/cyan] {message}")

    def print_warning(self, message: str):
        """Print warning message"""
        self.console.print(f"[yellow]⚠[/yellow] {message}")
