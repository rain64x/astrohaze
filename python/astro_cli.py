#!/usr/bin/env python3
"""
Vedic Astrology Interactive CLI
Interactive terminal application for Vedic astrology chart calculation and AI interpretation
"""

import sys
from datetime import datetime
import pytz
from geopy.geocoders import Nominatim
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
import json
import os

from vedic_calculator import VedicCalculator
from divisional_charts import DivisionalCharts
from yoga_detector import YogaDetector
from ai_interpreter import AIInterpreter
from chart_display import ChartDisplay


class AstroCLI:
    """Interactive CLI for Vedic astrology"""

    def __init__(self):
        """Initialize CLI application"""
        self.display = ChartDisplay()
        self.calculator = VedicCalculator()
        self.div_charts = DivisionalCharts()
        self.yoga_detector = YogaDetector()
        self.ai = AIInterpreter()
        self.current_chart = None
        self.current_yogas = None
        self.geolocator = Nominatim(user_agent="astrohaze_vedic_astrology")

        # Chart storage directory
        self.charts_dir = os.path.expanduser("~/.astrohaze/charts")
        os.makedirs(self.charts_dir, exist_ok=True)

    def geocode_location(self, location_name: str) -> tuple:
        """
        Geocode a location name to coordinates

        Returns:
            Tuple of (latitude, longitude, timezone_name) or None
        """
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                progress.add_task(description="Looking up location...", total=None)
                location = self.geolocator.geocode(location_name)

            if location:
                # Try to determine timezone (simplified - you may want to use timezonefinder)
                return location.latitude, location.longitude, "UTC"
            else:
                return None

        except Exception as e:
            self.display.print_error(f"Error geocoding location: {e}")
            return None

    def input_birth_details(self):
        """Collect birth details from user"""
        self.display.console.print("\n[bold cyan]Enter Birth Details[/bold cyan]\n")

        # Name
        name = Prompt.ask("[yellow]Name[/yellow]")

        # Date
        date_str = Prompt.ask(
            "[yellow]Birth Date[/yellow]",
            default="1990-01-01"
        )

        # Time
        time_str = Prompt.ask(
            "[yellow]Birth Time (HH:MM)[/yellow]",
            default="12:00"
        )

        # Combine date and time
        try:
            dt_str = f"{date_str} {time_str}"
            birth_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        except ValueError:
            self.display.print_error("Invalid date/time format")
            return None

        # Location
        use_geocoding = Confirm.ask(
            "[yellow]Would you like to search for your birth location by name?[/yellow]",
            default=True
        )

        if use_geocoding:
            location_name = Prompt.ask("[yellow]Birth Location (city, country)[/yellow]")
            geocode_result = self.geocode_location(location_name)

            if geocode_result:
                latitude, longitude, tz_name = geocode_result
                self.display.print_success(f"Found: {location_name} ({latitude:.2f}, {longitude:.2f})")
            else:
                self.display.print_error("Location not found, please enter coordinates manually")
                return None
        else:
            # Manual coordinates
            latitude = float(Prompt.ask("[yellow]Latitude[/yellow]", default="0.0"))
            longitude = float(Prompt.ask("[yellow]Longitude[/yellow]", default="0.0"))

        # Make datetime timezone-aware (simplified - using UTC)
        birth_dt = birth_dt.replace(tzinfo=pytz.UTC)

        return {
            'name': name,
            'birth_datetime': birth_dt,
            'latitude': latitude,
            'longitude': longitude
        }

    def calculate_chart(self, birth_details: dict):
        """Calculate complete birth chart"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task(description="Calculating birth chart...", total=None)

            # Calculate main chart
            chart_data = self.calculator.calculate_chart(
                birth_details['birth_datetime'],
                birth_details['latitude'],
                birth_details['longitude']
            )

            # Add name to chart data
            chart_data['name'] = birth_details['name']

            # Detect yogas
            progress.update(task, description="Detecting planetary yogas...")
            yogas_data = self.yoga_detector.detect_all_yogas(chart_data)

            self.current_chart = chart_data
            self.current_yogas = yogas_data

        self.display.print_success("Chart calculated successfully!")
        return chart_data, yogas_data

    def save_chart(self):
        """Save current chart to file"""
        if not self.current_chart:
            self.display.print_error("No chart to save")
            return

        filename = f"{self.current_chart['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json"
        filepath = os.path.join(self.charts_dir, filename)

        data_to_save = {
            'chart': self.current_chart,
            'yogas': self.current_yogas
        }

        try:
            with open(filepath, 'w') as f:
                json.dump(data_to_save, f, indent=2, default=str)

            self.display.print_success(f"Chart saved to: {filepath}")
        except Exception as e:
            self.display.print_error(f"Error saving chart: {e}")

    def load_chart(self):
        """Load a saved chart"""
        charts = os.listdir(self.charts_dir)
        json_charts = [c for c in charts if c.endswith('.json')]

        if not json_charts:
            self.display.print_warning("No saved charts found")
            return

        self.display.console.print("\n[bold cyan]Saved Charts:[/bold cyan]\n")
        for i, chart in enumerate(json_charts, 1):
            self.display.console.print(f"  {i}. {chart}")

        choice = Prompt.ask("\nSelect chart number", default="1")

        try:
            chart_file = json_charts[int(choice) - 1]
            filepath = os.path.join(self.charts_dir, chart_file)

            with open(filepath, 'r') as f:
                data = json.load(f)

            self.current_chart = data['chart']
            self.current_yogas = data.get('yogas')

            self.display.print_success(f"Loaded chart: {chart_file}")

        except Exception as e:
            self.display.print_error(f"Error loading chart: {e}")

    def show_main_menu(self):
        """Display main menu"""
        options = [
            "View Birth Chart",
            "View Dasha Periods",
            "View Divisional Charts (D9, D10, D12)",
            "Check Planetary Yogas",
            "Get AI Chart Interpretation",
            "Ask AI a Question",
            "Get Career Guidance",
            "Get Remedy Suggestions",
            "Save Chart",
            "Load Saved Chart",
            "Calculate New Chart"
        ]

        self.display.display_menu("Vedic Astrology Menu", options)

    def run_menu_action(self, choice: str):
        """Execute menu choice"""
        if not self.current_chart and choice not in ['10', '11']:
            self.display.print_warning("Please calculate or load a chart first")
            return True

        if choice == '1':
            self.display.display_full_chart(self.current_chart, self.current_yogas)

        elif choice == '2':
            self.display.console.print("\n")
            self.display.console.print(self.display.display_dasha_periods(self.current_chart['dasha']))
            self.display.console.print("\n")

        elif choice == '3':
            self.show_divisional_charts()

        elif choice == '4':
            if self.current_yogas:
                self.display.console.print("\n")
                self.display.console.print(self.display.display_yogas_panel(self.current_yogas))
                self.display.console.print("\n")

        elif choice == '5':
            self.get_chart_interpretation()

        elif choice == '6':
            self.ask_ai_question()

        elif choice == '7':
            self.get_career_guidance()

        elif choice == '8':
            self.get_remedy_suggestions()

        elif choice == '9':
            self.save_chart()

        elif choice == '10':
            self.load_chart()

        elif choice == '11':
            self.new_chart()

        elif choice == '0':
            return False

        else:
            self.display.print_error("Invalid choice")

        return True

    def show_divisional_charts(self):
        """Display divisional charts"""
        chart_types = ['D9', 'D10', 'D12']

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Calculating divisional charts...", total=None)

            div_charts = self.div_charts.get_all_divisional_charts(
                self.current_chart['planets'],
                chart_types
            )

        self.display.console.print("\n")
        for chart_type, chart_data in div_charts.items():
            self.display.console.print(self.display.display_divisional_chart(chart_data))
            self.display.console.print("\n")

    def get_chart_interpretation(self):
        """Get AI interpretation of the chart"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Generating AI interpretation...", total=None)

            interpretation = self.ai.interpret_chart_overview(self.current_chart)

        self.display.display_interpretation("Birth Chart Interpretation", interpretation)

    def ask_ai_question(self):
        """Ask AI a question about the chart"""
        question = Prompt.ask("\n[yellow]What would you like to know about this chart?[/yellow]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Getting AI response...", total=None)

            answer = self.ai.answer_question(question, self.current_chart)

        self.display.display_interpretation("AI Response", answer)

    def get_career_guidance(self):
        """Get career guidance from AI"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Generating career guidance...", total=None)

            guidance = self.ai.get_career_guidance(self.current_chart)

        self.display.display_interpretation("Career Guidance", guidance)

    def get_remedy_suggestions(self):
        """Get remedy suggestions from AI"""
        has_specific_issue = Confirm.ask(
            "\n[yellow]Do you have a specific issue you'd like remedies for?[/yellow]",
            default=False
        )

        specific_issue = None
        if has_specific_issue:
            specific_issue = Prompt.ask("[yellow]What issue would you like remedies for?[/yellow]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Generating remedy suggestions...", total=None)

            remedies = self.ai.suggest_remedies(self.current_chart, specific_issue)

        title = "Remedy Suggestions"
        if specific_issue:
            title += f" for {specific_issue}"

        self.display.display_interpretation(title, remedies)

    def new_chart(self):
        """Calculate a new chart"""
        birth_details = self.input_birth_details()
        if birth_details:
            self.calculate_chart(birth_details)

    def run(self):
        """Run the CLI application"""
        # Display welcome banner
        self.display.console.print("\n")
        self.display.console.print(
            "[bold cyan]╔══════════════════════════════════════════════╗[/bold cyan]"
        )
        self.display.console.print(
            "[bold cyan]║    ASTROHAZE - Vedic Astrology System      ║[/bold cyan]"
        )
        self.display.console.print(
            "[bold cyan]║    Powered by AI (Ollama + Llama 3.2)       ║[/bold cyan]"
        )
        self.display.console.print(
            "[bold cyan]╚══════════════════════════════════════════════╝[/bold cyan]"
        )
        self.display.console.print("\n")

        # Check if we should load existing chart or create new one
        has_saved_charts = len([f for f in os.listdir(self.charts_dir) if f.endswith('.json')]) > 0

        if has_saved_charts:
            load_existing = Confirm.ask(
                "[yellow]Would you like to load a saved chart?[/yellow]",
                default=False
            )
            if load_existing:
                self.load_chart()

        if not self.current_chart:
            self.display.console.print("[cyan]Let's calculate your birth chart![/cyan]\n")
            birth_details = self.input_birth_details()

            if not birth_details:
                self.display.print_error("Failed to get birth details")
                return

            self.calculate_chart(birth_details)

        # Main menu loop
        while True:
            self.show_main_menu()
            choice = Prompt.ask("[yellow]Select an option[/yellow]", default="1")

            should_continue = self.run_menu_action(choice)

            if not should_continue:
                self.display.console.print("\n[bold cyan]Thank you for using AstroHaze![/bold cyan]\n")
                break


def main():
    """Main entry point"""
    try:
        cli = AstroCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
