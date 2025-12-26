"""
AI Interpreter for Vedic Astrology
Uses Ollama (local LLM) to generate interpretations of astrological data
"""

import ollama
from typing import Dict, Optional
import json
from prompts import (
    get_chart_overview_prompt,
    get_planet_interpretation_prompt,
    get_dasha_interpretation_prompt,
    get_yoga_interpretation_prompt,
    get_divisional_chart_prompt,
    get_question_answer_prompt,
    get_career_guidance_prompt,
    get_remedy_suggestions_prompt
)


class AIInterpreter:
    """Generate AI-powered interpretations of Vedic astrology charts using Ollama"""

    def __init__(self, model_name: str = "llama3.2", temperature: float = 0.7):
        """
        Initialize AI interpreter

        Args:
            model_name: Name of Ollama model to use (default: llama3.2)
            temperature: Creativity level (0.0-1.0, default: 0.7)
        """
        self.model_name = model_name
        self.temperature = temperature
        self.ollama_available = self.check_ollama_availability()

    def check_ollama_availability(self) -> bool:
        """Check if Ollama is installed and running"""
        try:
            # Try to list models to check if Ollama is available
            ollama.list()
            return True
        except Exception as e:
            print(f"Warning: Ollama not available - {e}")
            print("Please install Ollama from https://ollama.ai and run: ollama pull llama3.2")
            return False

    def generate_interpretation(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Generate interpretation using Ollama

        Args:
            prompt: The prompt to send to the AI
            max_tokens: Maximum length of response

        Returns:
            AI-generated interpretation text
        """
        if not self.ollama_available:
            return self.get_fallback_response()

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are an expert Vedic astrologer with deep knowledge of classical texts like BPHS, Jaimini, and Phaladeepika. Provide insightful, practical, and encouraging interpretations.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'temperature': self.temperature,
                    'num_predict': max_tokens
                }
            )

            return response['message']['content']

        except Exception as e:
            print(f"Error generating interpretation: {e}")
            return self.get_fallback_response()

    def get_fallback_response(self) -> str:
        """Return fallback response when AI is not available"""
        return """AI interpretation not available. Please ensure Ollama is installed and running.

Install Ollama:
1. Visit https://ollama.ai
2. Download and install Ollama
3. Run: ollama pull llama3.2
4. Ollama will start automatically

The astrological calculations are still accurate - only AI interpretations are unavailable."""

    def interpret_chart_overview(self, chart_data: Dict) -> str:
        """
        Generate overall chart interpretation

        Args:
            chart_data: Complete birth chart data

        Returns:
            Comprehensive interpretation
        """
        prompt = get_chart_overview_prompt(chart_data)
        return self.generate_interpretation(prompt, max_tokens=1500)

    def interpret_planet_placement(
        self,
        planet: str,
        sign: str,
        nakshatra: str,
        house: int
    ) -> str:
        """
        Interpret specific planet placement

        Args:
            planet: Planet name
            sign: Zodiac sign
            nakshatra: Nakshatra name
            house: House number

        Returns:
            Planet-specific interpretation
        """
        prompt = get_planet_interpretation_prompt(planet, sign, nakshatra, house)
        return self.generate_interpretation(prompt, max_tokens=800)

    def interpret_dasha_period(
        self,
        dasha_period: Dict,
        birth_chart: Dict
    ) -> str:
        """
        Interpret Vimshottari Dasha period

        Args:
            dasha_period: Dasha period data
            birth_chart: Complete birth chart

        Returns:
            Dasha interpretation
        """
        prompt = get_dasha_interpretation_prompt(dasha_period, birth_chart)
        return self.generate_interpretation(prompt, max_tokens=1000)

    def interpret_yogas(self, yogas: list) -> str:
        """
        Interpret detected yogas

        Args:
            yogas: List of detected yogas

        Returns:
            Yogas interpretation
        """
        if not yogas:
            return "No significant yogas detected in this chart. This doesn't mean a bad chart - it simply means no classical yoga combinations are present."

        prompt = get_yoga_interpretation_prompt(yogas)
        return self.generate_interpretation(prompt, max_tokens=1200)

    def interpret_divisional_chart(
        self,
        chart_type: str,
        signification: str,
        positions: Dict
    ) -> str:
        """
        Interpret divisional chart

        Args:
            chart_type: Type (D9, D10, etc.)
            signification: What the chart represents
            positions: Planetary positions in divisional chart

        Returns:
            Divisional chart interpretation
        """
        prompt = get_divisional_chart_prompt(chart_type, signification, positions)
        return self.generate_interpretation(prompt, max_tokens=1000)

    def answer_question(self, question: str, chart_data: Dict) -> str:
        """
        Answer specific question about the chart

        Args:
            question: User's question
            chart_data: Complete birth chart

        Returns:
            Answer to the question
        """
        prompt = get_question_answer_prompt(question, chart_data)
        return self.generate_interpretation(prompt, max_tokens=800)

    def get_career_guidance(self, chart_data: Dict) -> str:
        """
        Provide career guidance based on chart

        Args:
            chart_data: Complete birth chart

        Returns:
            Career guidance
        """
        prompt = get_career_guidance_prompt(chart_data)
        return self.generate_interpretation(prompt, max_tokens=1000)

    def suggest_remedies(
        self,
        chart_data: Dict,
        specific_issue: Optional[str] = None
    ) -> str:
        """
        Suggest astrological remedies

        Args:
            chart_data: Complete birth chart
            specific_issue: Specific problem to address (optional)

        Returns:
            Remedy suggestions
        """
        prompt = get_remedy_suggestions_prompt(chart_data, specific_issue)
        return self.generate_interpretation(prompt, max_tokens=1000)

    def chat_about_chart(
        self,
        chart_data: Dict,
        conversation_history: list = None
    ) -> str:
        """
        Have a conversational interaction about the chart

        Args:
            chart_data: Complete birth chart
            conversation_history: Previous messages in conversation

        Returns:
            AI response
        """
        if conversation_history is None:
            conversation_history = []

        if not self.ollama_available:
            return self.get_fallback_response()

        # Build chart context
        planets = chart_data['planets']
        chart_context = f"""Birth Chart Context:
Ascendant: {planets['Ascendant']['sign']}
Sun: {planets['Sun']['sign']}
Moon: {planets['Moon']['sign']} ({planets['Moon']['nakshatra']['nakshatra']} nakshatra)
"""

        messages = [
            {
                'role': 'system',
                'content': f"""You are an expert Vedic astrologer. You are discussing a birth chart with someone. Here's their chart data:

{chart_context}

Provide insightful, practical guidance based on Vedic astrology principles. Be conversational and friendly."""
            }
        ]

        # Add conversation history
        messages.extend(conversation_history)

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options={
                    'temperature': self.temperature,
                    'num_predict': 800
                }
            )

            return response['message']['content']

        except Exception as e:
            print(f"Error in chat: {e}")
            return self.get_fallback_response()


# Helper function for quick interpretations
def quick_interpret(chart_data: Dict, interpretation_type: str = "overview") -> str:
    """
    Quick interpretation helper

    Args:
        chart_data: Birth chart data
        interpretation_type: Type of interpretation (overview, career, remedies)

    Returns:
        Interpretation text
    """
    interpreter = AIInterpreter()

    if interpretation_type == "overview":
        return interpreter.interpret_chart_overview(chart_data)
    elif interpretation_type == "career":
        return interpreter.get_career_guidance(chart_data)
    elif interpretation_type == "remedies":
        return interpreter.suggest_remedies(chart_data)
    else:
        return "Unknown interpretation type"
