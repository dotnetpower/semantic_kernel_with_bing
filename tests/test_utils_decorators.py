"""
Test the utility decorators module.
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import patch

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.decorators import measure_time_async


async def test_measure_time_async():
    """Test the measure_time_async decorator works correctly."""
    
    @measure_time_async
    async def sample_async_function(return_value="test"):
        """A sample async function for testing."""
        await asyncio.sleep(0.01)  # Sleep for 10ms
        return return_value
    
    # Test with capture of printed output
    with patch('builtins.print') as mock_print:
        result = await sample_async_function("hello")
        
        # Verify the function returned correctly
        assert result == "hello"
        
        # Verify print was called with timing information
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        assert "sample_async_function elapsed:" in call_args
        assert "s" in call_args  # Should end with 's' for seconds
        
        print("✓ measure_time_async decorator test passed")


async def test_measure_time_async_with_args():
    """Test the measure_time_async decorator works with function arguments."""
    
    @measure_time_async
    async def function_with_args(a, b, c=None):
        """A sample async function with arguments."""
        await asyncio.sleep(0.01)
        return f"{a}-{b}-{c}"
    
    # Test with capture of printed output
    with patch('builtins.print') as mock_print:
        result = await function_with_args("arg1", "arg2", c="kwarg")
        
        # Verify the function returned correctly
        assert result == "arg1-arg2-kwarg"
        
        # Verify print was called with timing information
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        assert "function_with_args elapsed:" in call_args
        
        print("✓ measure_time_async decorator with args test passed")


if __name__ == "__main__":
    asyncio.run(test_measure_time_async())
    asyncio.run(test_measure_time_async_with_args())
    print("All tests passed!")