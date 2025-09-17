# Utils Module

This module contains utility functions and decorators that can be used across the project.

## Decorators

### `measure_time_async`

A decorator that measures the execution time of async functions and prints the elapsed time.

#### Usage

```python
from utils.decorators import measure_time_async
# or
from utils import measure_time_async

@measure_time_async
async def my_async_function():
    await asyncio.sleep(1)
    return "done"

# Output: my_async_function elapsed: 1.0012s
```

#### Features

- Works with any async function
- Preserves function metadata using `functools.wraps`
- Prints execution time with 4 decimal precision
- Returns the original function result unchanged
- Works with functions that have arguments and keyword arguments

#### Example

```python
import asyncio
from utils import measure_time_async

class MyService:
    @measure_time_async
    async def fetch_data(self, data_id: str):
        # Simulate network call
        await asyncio.sleep(0.5)
        return f"Data for {data_id}"

async def main():
    service = MyService()
    result = await service.fetch_data("123")
    # Output: fetch_data elapsed: 0.5001s
    print(result)  # Data for 123

asyncio.run(main())
```

This decorator was extracted from the `GroundingWithBingSearch` class to make it reusable across the entire project.