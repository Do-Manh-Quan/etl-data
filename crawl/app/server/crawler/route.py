from typing import List
from fastapi import APIRouter, Body, HTTPException, BackgroundTasks
from server.crawler.model import CrawlerSchema
from server.crawler.crawlerAliexpress import crawl_aliexpress_store
from server.crawler.crawlerLangchain import crawl_google_store
from server.database import database
from bson import ObjectId
from typing import Any, Union
from server.crawler.model import Status, Type
from datetime import datetime
from server.FilterModule.app import getDocumentsNotFilter, handleFilter
router = APIRouter()
collection = database.crawler 
import asyncio

def convert_to_json_compatible(data: Any) -> Union[dict, list]:
    if isinstance(data, dict):
        return {key: convert_to_json_compatible(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_to_json_compatible(item) for item in data]
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data

@router.post("/", response_description="crawler data added into the database", status_code=201)
async def add_crawler_data(crawler: CrawlerSchema = Body(...)):
    check_url = await collection.find_one({"url": crawler.url})
    if check_url:
        raise HTTPException(status_code=409, detail="URL already exists in the database.")  # Use raise to trigger HTTPException

    inserted_result = await collection.insert_one(crawler.dict())
    inserted_id = inserted_result.inserted_id
    
    inserted_document = await collection.find_one({"_id": inserted_id})
    if inserted_document is None:
        raise HTTPException(status_code=404, detail="Inserted document not found.")

    json_compatible_document = convert_to_json_compatible(inserted_document)
    
    return {
        "message": "Crawler added successfully.",
        "data": json_compatible_document
    }
@router.get("/", response_description="crawlers retrieved", status_code=200)
async def get_crawlers():
    crawlers = []
    async for student in collection.find():
        crawlers.append(convert_to_json_compatible(student))
    return crawlers

async def crawl(url: str, type):
    # Simulate a crawling process with sleep
    if type == Type.aliexpress:
        await crawl_aliexpress_store(url=url)
    else:
        await crawl_google_store(url=url)

@router.get("/start", response_description="Start the crawler", status_code=202)
async def start_crawler_endpoint(background_tasks: BackgroundTasks):
    return await start_crawler(background_tasks)
async def start_crawler(background_tasks: BackgroundTasks, is_auto_trigger: bool = False):
    latest_queue_crawler = await collection.find({"status": Status.queue}).sort("updated_at", -1).limit(1).to_list(1)
    if latest_queue_crawler:
        latest_queue_crawler = latest_queue_crawler[0]
    else:
        latest_queue_crawler = None
    if not latest_queue_crawler:
        page_number = 0 
        page_size = 10 
        productsNotFilter = getDocumentsNotFilter(page_number, page_size)
        handleFilter(productsNotFilter)
        while len(productsNotFilter) == page_size:
            productsNotFilter = getDocumentsNotFilter(page_number, page_size)
            handleFilter(productsNotFilter)
        if is_auto_trigger:
            return
        raise HTTPException(status_code=404, detail="Crawler not found.")

    await collection.update_one(
        {"_id": latest_queue_crawler["_id"]},
        {"$set": {"status": Status.start, "updated_at": datetime.now()}}
    )

    background_tasks.add_task(execute_crawler, str(latest_queue_crawler["_id"]),str(latest_queue_crawler["type"]), latest_queue_crawler["url"], background_tasks)

    return {"message": "Crawler started."}

async def execute_crawler(crawler_id: str,type: str, url: str,background_tasks):
    try:
        await crawl(url, type)
        await collection.update_one(
            {"_id": ObjectId(crawler_id)},
            {"$set": {"status": Status.complete, "updated_at": datetime.now()}}
        )
        print(str(crawler_id))
        print('complete')
        background_tasks.add_task(start_crawler, background_tasks, True)


    except Exception as e:
        await collection.update_one(
            {"_id": ObjectId(crawler_id)},
            {"$set": {"status": Status.stop, "updated_at": datetime.now()}}
        )
        print(str(crawler_id))
        print('stop')
        raise e
@router.get("/{url}", response_description="crawler data retrieved", status_code=200)
async def get_crawler_data(url: str):
    crawler = await collection.find_one({"url": url})
    if crawler:
        return convert_to_json_compatible(crawler) 
    raise HTTPException(status_code=404, detail="crawler not found")

@router.put("/{url}", response_description="crawler data updated", status_code=200)
async def update_crawler_data(url: str, req: CrawlerSchema = Body(...)):
    updated_crawler = await collection.update_one({"url": url}, {"$set": req.dict()})
    if updated_crawler.modified_count == 1:
        return {"message": "crawler with url: {} updated successfully".format(url)}
    raise HTTPException(status_code=404, detail="crawler not found")

@router.delete("/{id}", response_description="crawler data deleted from the database", status_code=200)
async def delete_crawler_data(id: str):
    deleted_crawler = await collection.delete_one({"_id": ObjectId(id)})
    if deleted_crawler.deleted_count == 1:
        return {"message": "crawler with id: {} deleted successfully".format(id)}
    raise HTTPException(status_code=404, detail="crawler not found")
