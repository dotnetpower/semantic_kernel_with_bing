#!/usr/bin/env python3
"""
Example usage of the measure_time_async utility function.

This demonstrates how other Python files can import and use the
measure_time_async decorator from the utils.decorators module.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.decorators import measure_time_async


class ExampleService:
    """Example service demonstrating usage of measure_time_async decorator."""
    
    @measure_time_async
    async def fetch_data(self, data_id: str):
        """Simulate fetching data from an external service."""
        print(f"Fetching data for ID: {data_id}")
        await asyncio.sleep(0.5)  # Simulate network call
        return f"Data for {data_id}"
    
    @measure_time_async
    async def process_data(self, data: str):
        """Simulate processing the fetched data."""
        print(f"Processing: {data}")
        await asyncio.sleep(0.2)  # Simulate processing time
        return f"Processed {data}"
    
    async def run_workflow(self):
        """Run a complete workflow with timing."""
        print("Starting workflow...")
        
        # Both methods will be timed automatically
        data = await self.fetch_data("12345")
        result = await self.process_data(data)
        
        print(f"Final result: {result}")
        return result


async def standalone_function(name: str):
    """A standalone function using the decorator."""
    print(f"Hello, {name}!")
    await asyncio.sleep(0.1)
    return f"Greeted {name}"


# Apply decorator to standalone function
standalone_function = measure_time_async(standalone_function)


async def main():
    """Main function demonstrating usage."""
    print("=" * 50)
    print("Example usage of measure_time_async utility")
    print("=" * 50)
    
    # Test service methods
    service = ExampleService()
    await service.run_workflow()
    
    print("\n" + "-" * 30)
    
    # Test standalone function
    await standalone_function("World")
    
    print("\n✓ All examples completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())