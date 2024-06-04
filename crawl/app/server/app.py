from fastapi import FastAPI

from server.product.route import router as ProductRouter
from server.crawler.route import router as CrawlerRouter

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(CrawlerRouter, tags=["Crawler"], prefix="/crawler")
app.include_router(ProductRouter, tags=["Product"], prefix="/product")