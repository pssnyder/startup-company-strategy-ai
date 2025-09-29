#!/usr/bin/env python3
"""
Startup Company Real-Time AI Advisor
Main entry point for the real-time game monitoring and AI strategy system.
"""

import os
import sys
from pathlib import Path

# Add the ai_advisor package to Python path
sys.path.insert(0, str(Path(__file__).parent))

from ai_advisor.real_time_monitor import RealTimeGameAdvisor


def main():
    """Main entry point."""
    print("🎮 Startup Company Real-Time AI Advisor")
    print("========================================")
    
    # Default save directory path
    default_save_path = r"C:\Users\patss\Saved Games\Startup Company\testing_v1"
    
    # Check if save directory exists
    if not Path(default_save_path).exists():
        print(f"❌ Save directory not found: {default_save_path}")
        print("Please update the path in startup_monitor.py or provide it as an argument.")
        return
    
    # Get Gemini API key from environment or prompt
    gemini_key = os.environ.get('GEMINI_API_KEY')
    if not gemini_key:
        print("⚠️ No Gemini API key found in environment variable GEMINI_API_KEY")
        print("AI strategy features will be limited to fallback mode.")
        print("To enable full AI features, set your API key:")
        print("export GEMINI_API_KEY='your-api-key-here'")
        print()
    
    # Initialize and start the advisor
    advisor = RealTimeGameAdvisor(
        save_directory=default_save_path,
        output_directory="game_saves",
        gemini_api_key=gemini_key
    )
    
    try:
        # Start monitoring with 5-minute AI analysis intervals
        advisor.start_monitoring(ai_analysis_interval=300)
    except KeyboardInterrupt:
        print("\n👋 Goodbye! Your game data has been saved.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Check the logs in game_saves/file_watcher.log for details.")


if __name__ == "__main__":
    main()