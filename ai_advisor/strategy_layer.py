"""
Strategy Layer: AI-Powered Strategic Analysis

This module integrates with Google's Gemini API to provide intelligent
strategic recommendations based on the analyzed game state.
"""

import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .calculation_layer import GameStateAnalyzer, StrategicAlert, ComponentShortfall


@dataclass
class StrategicRecommendation:
    """AI-generated strategic recommendation."""
    priority: int
    action_type: str  # "immediate", "short_term", "long_term"
    title: str
    description: str
    expected_outcome: str
    time_frame: str
    resources_needed: List[str]


@dataclass
class AIInsight:
    """Complete AI analysis result."""
    overall_assessment: str
    risk_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    key_recommendations: List[StrategicRecommendation]
    production_priorities: List[str]
    financial_advice: str
    next_steps: List[str]


class GeminiStrategyAdvisor:
    """AI-powered strategy advisor using Google's Gemini API."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        self.system_persona = self._get_system_persona()
    
    def _get_system_persona(self) -> str:
        """Define the AI persona for strategic advice."""
        return """You are an elite strategic Product Owner and business consultant specializing in startup management and operational efficiency. 

Your expertise includes:
- Identifying critical business risks and opportunities
- Optimizing resource allocation and team productivity  
- Strategic financial planning and runway management
- Product development prioritization
- Crisis management and rapid problem-solving

Your communication style is:
- Concise and actionable
- Data-driven with clear reasoning
- Focused on practical solutions
- Confident but not overconfident
- Emphasizes both immediate fixes AND long-term strategy

Always provide specific, measurable recommendations with clear timelines and expected outcomes."""
    
    async def generate_strategy(self, analyzer: GameStateAnalyzer) -> Optional[AIInsight]:
        """Generate comprehensive strategic recommendations."""
        if not self.api_key:
            return self._generate_fallback_strategy(analyzer)
        
        try:
            # Build context from analysis
            context = analyzer.get_ai_strategy_context()
            analysis_data = analyzer.analyze()
            
            # Create structured prompt
            prompt = self._build_strategic_prompt(context, analysis_data)
            
            # Call Gemini API
            response = await self._call_gemini_api(prompt)
            
            if response:
                return self._parse_ai_response(response, analysis_data)
            else:
                return self._generate_fallback_strategy(analyzer)
                
        except Exception as e:
            print(f"Error generating AI strategy: {e}")
            return self._generate_fallback_strategy(analyzer)
    
    def _build_strategic_prompt(self, context: str, analysis_data: Dict[str, Any]) -> str:
        """Build a structured prompt for the AI."""
        alerts_summary = self._summarize_alerts(analysis_data.get('alerts', []))
        shortfalls_summary = self._summarize_shortfalls(analysis_data.get('component_shortfalls', []))
        
        prompt = f"""
STRATEGIC ANALYSIS REQUEST

CURRENT SITUATION:
{context}

IDENTIFIED ISSUES:
{alerts_summary}

RESOURCE SHORTFALLS:
{shortfalls_summary}

TASK: Provide a comprehensive 5-day strategic action plan that addresses:

1. IMMEDIATE ACTIONS (Next 24-48 hours):
   - Critical issues requiring urgent attention
   - Resource allocation decisions
   - Risk mitigation steps

2. SHORT-TERM STRATEGY (Days 3-5):
   - Production planning priorities
   - Team optimization
   - Performance improvements

3. FINANCIAL PLANNING:
   - Cash flow management
   - Runway extension strategies
   - Investment priorities

4. SUCCESS METRICS:
   - How to measure progress
   - Key performance indicators to track
   - Decision points for strategy adjustments

Format your response as a structured JSON with the following fields:
- overall_assessment: string (2-3 sentences)
- risk_level: "LOW"|"MEDIUM"|"HIGH"|"CRITICAL"
- key_recommendations: array of {{priority, action_type, title, description, expected_outcome, time_frame, resources_needed}}
- production_priorities: array of strings (top 5 production tasks)
- financial_advice: string (specific financial guidance)
- next_steps: array of strings (actionable next steps)
"""
        return prompt
    
    async def _call_gemini_api(self, prompt: str) -> Optional[str]:
        """Make API call to Gemini."""
        try:
            headers = {
                'Content-Type': 'application/json',
            }
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": f"{self.system_persona}\n\n{prompt}"
                            }
                        ]
                    }
                ]
            }
            
            url = f"{self.base_url}?key={self.api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['candidates'][0]['content']['parts'][0]['text']
                    else:
                        print(f"Gemini API error: {response.status}")
                        return None
                        
        except Exception as e:
            print(f"API call error: {e}")
            return None
    
    def _parse_ai_response(self, response: str, analysis_data: Dict[str, Any]) -> AIInsight:
        """Parse the AI response into structured recommendations."""
        try:
            # Try to extract JSON from the response
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                json_str = response
            
            ai_data = json.loads(json_str)
            
            # Convert to structured recommendations
            recommendations = []
            for rec_data in ai_data.get('key_recommendations', []):
                recommendations.append(StrategicRecommendation(
                    priority=rec_data.get('priority', 1),
                    action_type=rec_data.get('action_type', 'immediate'),
                    title=rec_data.get('title', ''),
                    description=rec_data.get('description', ''),
                    expected_outcome=rec_data.get('expected_outcome', ''),
                    time_frame=rec_data.get('time_frame', ''),
                    resources_needed=rec_data.get('resources_needed', [])
                ))
            
            return AIInsight(
                overall_assessment=ai_data.get('overall_assessment', ''),
                risk_level=ai_data.get('risk_level', 'MEDIUM'),
                key_recommendations=recommendations,
                production_priorities=ai_data.get('production_priorities', []),
                financial_advice=ai_data.get('financial_advice', ''),
                next_steps=ai_data.get('next_steps', [])
            )
            
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            return self._create_fallback_insight(analysis_data)
    
    def _generate_fallback_strategy(self, analyzer: GameStateAnalyzer) -> AIInsight:
        """Generate basic strategy when AI is unavailable."""
        analysis_data = analyzer.analyze()
        return self._create_fallback_insight(analysis_data)
    
    def _create_fallback_insight(self, analysis_data: Dict[str, Any]) -> AIInsight:
        """Create a basic strategic insight based on rule-based analysis."""
        alerts = analysis_data.get('alerts', [])
        shortfalls = analysis_data.get('component_shortfalls', [])
        metrics = analysis_data.get('metrics_summary', {})
        
        # Determine risk level
        critical_alerts = [a for a in alerts if a.severity == "CRITICAL"]
        if critical_alerts:
            risk_level = "CRITICAL"
        elif len([a for a in alerts if a.severity == "HIGH"]) > 2:
            risk_level = "HIGH"
        else:
            risk_level = "MEDIUM"
        
        # Basic recommendations
        recommendations = []
        
        # Satisfaction fix
        if metrics.get('user_satisfaction', 100) < 50:
            recommendations.append(StrategicRecommendation(
                priority=1,
                action_type="immediate",
                title="Fix User Satisfaction Crisis",
                description="Upgrade Landing Page and other key features to improve satisfaction",
                expected_outcome="Increase satisfaction above 75%",
                time_frame="24-48 hours",
                resources_needed=["Developers", "Designers", "Components"]
            ))
        
        # Production priorities
        production_priorities = []
        for shortfall in shortfalls[:5]:
            production_priorities.append(f"{shortfall.component_name} ({shortfall.needed_quantity} needed)")
        
        return AIInsight(
            overall_assessment=f"Company is in {risk_level.lower()} risk state with {len(critical_alerts)} critical issues requiring immediate attention.",
            risk_level=risk_level,
            key_recommendations=recommendations,
            production_priorities=production_priorities,
            financial_advice="Monitor cash flow closely and prioritize revenue-generating activities.",
            next_steps=[
                "Address critical satisfaction issues immediately",
                "Optimize component production pipeline",
                "Review financial runway and burn rate"
            ]
        )
    
    def _summarize_alerts(self, alerts: List[StrategicAlert]) -> str:
        """Summarize alerts for prompt."""
        if not alerts:
            return "No critical alerts identified."
        
        summary = []
        for alert in alerts[:5]:  # Top 5 alerts
            summary.append(f"- {alert.severity}: {alert.title} - {alert.description}")
        
        return "\n".join(summary)
    
    def _summarize_shortfalls(self, shortfalls: List[ComponentShortfall]) -> str:
        """Summarize component shortfalls for prompt."""
        if not shortfalls:
            return "No significant resource shortfalls identified."
        
        summary = []
        for shortfall in shortfalls[:5]:  # Top 5 shortfalls
            summary.append(f"- Need {shortfall.needed_quantity}x {shortfall.component_name} ({shortfall.employee_type}, {shortfall.total_hours_required:.1f}h)")
        
        return "\n".join(summary)