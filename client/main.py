"""
Main entry point for ChaseHome client
"""
import sys
import os
import logging

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from client.game import Game

def main():
    """Main function to start the ChaseHome client"""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting ChaseHome client...")
    
    try:
        # Create and run the game
        game = Game()
        game.run()
    except Exception as e:
        logger.error(f"Error running game: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("ChaseHome client stopped")

if __name__ == "__main__":
    main()