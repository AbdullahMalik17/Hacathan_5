import sys
from pathlib import Path
import asyncio

# Add project root to python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from backend.src.workers.message_processor import main

if __name__ == "__main__":
    asyncio.run(main())