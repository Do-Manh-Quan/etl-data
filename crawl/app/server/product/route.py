from typing import List
from fastapi import APIRouter, Body, HTTPException, Query
from server.product.model import AliexpressProductSchema
from server.database import database
from bson import ObjectId
from typing import Any, Union
router = APIRouter()
collection = database.products 

def convert_to_json_compatible(data: Any) -> Union[dict, list]:
    if isinstance(data, dict):
        return {key: convert_to_json_compatible(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_to_json_compatible(item) for item in data]
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data

@router.post("/", response_description="Product data added into the database", status_code=201)
async def add_product_data(product: AliexpressProductSchema = Body(...)):
    inserted_product = await collection.insert_one(product.dict())
    return {"message": "Product added successfully."}

@router.get("/", response_description="Products retrieved", status_code=200)
async def get_products():
    products = []
    async for student in collection.find():
        products.append(convert_to_json_compatible(student))
    return products

@router.get("/{id}", response_description="Product data retrieved", status_code=200)
async def get_product_data(id: str):
    product = await collection.find_one({"_id": ObjectId(id)})
    if product:
        return convert_to_json_compatible(product)
    raise HTTPException(status_code=404, detail="Product not found")

@router.put("/{id}", response_description="Product data updated", status_code=200)
async def update_product_data(id: str, req: AliexpressProductSchema = Body(...)):
    updated_product = await collection.update_one({"_id": id}, {"$set": req.dict()})
    if updated_product.modified_count == 1:
        return {"message": "Product with id: {} updated successfully".format(id)}
    raise HTTPException(status_code=404, detail="Product not found")

@router.delete("/{id}", response_description="Product data deleted from the database", status_code=200)
async def delete_product_data(id: str):
    deleted_product = await collection.delete_one({"_id": ObjectId(id)})
    if deleted_product.deleted_count == 1:
        return {"message": "Product with id: {} deleted successfully".format(id)}
    raise HTTPException(status_code=404, detail="Product not found")

@router.get("/search/", response_description="Search products by title", status_code=200)
async def search_products_by_title(title: str = Query(..., description="The title of the product to search for")):
    query = {"title": {"$regex": title, "$options": "i"}}
    products = []
    async for product in collection.find(query):
        products.append(convert_to_json_compatible(product))
    return {"products": products}

@router.get("/statistics/url", response_description="Get product statistics by URL", status_code=200)
async def get_product_statistics_by_url():
    pipeline = [
        {
            "$group": {
                "_id": {
                    "$let": {
                        "vars": {"rootUrl": {"$substr": [{"$arrayElemAt": [{"$split": ["$url", "/"]}, 2]}, 0, -1]}},
                        "in": "$$rootUrl"
                    }
                },
                "count": {"$sum": 1}
            }
        },
        {
            "$project": {
                "_id": 0,
                "root": "$_id",
                "count": 1
            }
        }
    ]
    
    cursor = collection.aggregate(pipeline)
    statistics = []
    async for document in cursor:
        statistics.append(convert_to_json_compatible(document))
    return {"statistics": statistics}