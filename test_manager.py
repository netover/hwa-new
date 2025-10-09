import asyncio
from resync.core.pools.pool_manager import get_connection_pool_manager, reset_connection_pool_manager

async def test_manager():
    try:
        manager = await get_connection_pool_manager()
        print(f'Manager initialized: {manager._initialized}')
        print(f'Pools: {list(manager.pools.keys())}')

        # Reset for next test
        await reset_connection_pool_manager()
        print('Manager reset successfully')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    asyncio.run(test_manager())
