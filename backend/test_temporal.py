import asyncio
from temporalio.client import Client

async def test():
    try:
        client = await Client.connect('temporal:7233')
        print('✅ Temporal is working!')
    except Exception as e:
        print(f'❌ Error: {e}')

asyncio.run(test())
