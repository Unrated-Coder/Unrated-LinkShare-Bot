from aiohttp import web
from .route import routes

async def web_server():
    web_app = web.Application()
    web_app.add_routes(routes)
    return web_app
