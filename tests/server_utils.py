import asyncio
from urllib.parse import urlsplit


async def get(url_str: str) -> str:
    await asyncio.sleep(0.01)
    url = urlsplit(url_str)
    reader, writer = await asyncio.open_connection(url.hostname, url.port)

    writer.write((f"GET {url.path or '/'} HTTP/1.0\r\n"
                  f"Host: {url.hostname}\r\n"
                  f"\r\n").encode('utf8'))
    response = await reader.read()
    await writer.drain()
    writer.close()
    await writer.wait_closed()
    return response.decode('utf8')
