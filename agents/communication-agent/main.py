#!/usr/bin/env python3
"""
Communication Intelligence Agent - Main Entry Point

This agent analyzes Webex chats, meeting transcripts, and emails to:
1. Separate conversations by customer vs internal
2. Extract action items with due dates
3. Prioritize based on urgency and context
"""

import argparse
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

from config import get_settings, OutputFormat
from agent import CommunicationAgent
from output_formatter import OutputFormatter


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Reduce noise from third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("msal").setLevel(logging.WARNING)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Communication Intelligence Agent - Extract actions from Webex and Email",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with all sources, last 7 days
  python main.py

  # Run with specific sources
  python main.py --sources webex_chat email

  # Run with 14 day lookback, verbose output
  python main.py --days 14 --verbose

  # Export to all formats
  python main.py --output-all

  # Use rule-based extraction (no LLM)
  python main.py --no-llm
        """
    )
    
    parser.add_argument(
        '--days', '-d',
        type=int,
        default=None,
        help='Number of days to look back (default: from config or 7)'
    )
    
    parser.add_argument(
        '--sources', '-s',
        nargs='+',
        choices=['webex_chat', 'webex_transcript', 'email'],
        default=None,
        help='Data sources to collect from (default: all)'
    )
    
    parser.add_argument(
        '--output', '-o',
        choices=['json', 'csv', 'markdown'],
        default=None,
        help='Output format (default: from config or json)'
    )
    
    parser.add_argument(
        '--output-all',
        action='store_true',
        help='Export to all formats (json, csv, markdown)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help='Output directory for reports'
    )
    
    parser.add_argument(
        '--no-llm',
        action='store_true',
        help='Use rule-based extraction instead of LLM'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress console output (only save to file)'
    )
    
    parser.add_argument(
        '--env-file',
        type=str,
        default='.env',
        help='Path to .env file (default: .env)'
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    env_path = Path(args.env_file)
    if env_path.exists():
        load_dotenv(env_path)
    else:
        print(f"Warning: Environment file '{args.env_file}' not found.")
        print("Please copy .env.example to .env and configure your credentials.")
        sys.exit(1)
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Load settings
        settings = get_settings()
        
        # Override settings from command line
        if args.output_dir:
            settings.output_dir = args.output_dir
        
        if args.output:
            settings.output_format = OutputFormat(args.output)
        
        # Create agent
        agent = CommunicationAgent(settings)
        
        # Run agent
        report = agent.run(
            lookback_days=args.days,
            use_llm=not args.no_llm,
            sources=args.sources
        )
        
        # Create formatter
        formatter = OutputFormatter(settings)
        
        # Print to console unless quiet mode
        if not args.quiet:
            formatter.print_console(report)
        
        # Save output
        if args.output_all:
            paths = formatter.save_all_formats(report)
            logger.info("Reports saved:")
            for fmt, path in paths.items():
                logger.info(f"  {fmt}: {path}")
        else:
            path = formatter.save(report)
            logger.info(f"Report saved to: {path}")
        
        # Exit with appropriate code
        if report.high_priority_count > 0:
            logger.warning(f"⚠️  {report.high_priority_count} high priority action(s) require attention!")
        
        if report.overdue_count > 0:
            logger.warning(f"⚠️  {report.overdue_count} action(s) are overdue!")
        
        sys.exit(0)
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Agent failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
