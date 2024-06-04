import os
from pymongo import MongoClient
import google.generativeai as genai
from bson import json_util
from bson import ObjectId
from flask import jsonify
import re
import sys
import codecs

# Thiết lập bộ mã hóa cho stdout
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
# URI kết nối SRV (thay thế <username>, <password>, và <cluster-url> bằng thông tin của bạn)
uri = "mongodb+srv://quanchopper1234:1234@cluster0.xyyijmh.mongodb.net?retryWrites=true&w=majority"

# Kết nối đến MongoDB Atlas
client = MongoClient(uri)

# Truy cập vào cơ sở dữ liệu
db = client['crawler']

# Truy cập vào collection
collection = db['products']

genai.configure(api_key="AIzaSyAKWIqNFsMYTkcnvbWU8KTUosuGBib79R4")
# The Gemini 1.5 models are versatile and work with both text-only and multimodal prompts
model = genai.GenerativeModel('gemini-1.5-flash')
schema = ""
FIELD_COMPARE_KEYWORD = "title"
KEYWORDS = "keywords"
def askGemini(prompt):
    if prompt:
      response = model.generate_content(prompt)
      return response
    return {"text": ""}



def getJsonDataFromResGemini(res):
    if (not res or res == ""):
        return {}
    start_index_tmp = res.find("```json\n{")
    # Trích xuất chuỗi JSON
    if start_index_tmp >= 0:
        start_index = start_index_tmp + len("```json\n")
        end_index_tmp = res.find("}\n```") 
        if end_index_tmp >= 0:
            end_index = end_index_tmp + 1
            json_str = res[start_index:end_index]
            jsondata = json_util.loads(json_str)
            return jsondata
        else:
            return {}
    return {}

def getDocumentsNotFilter(page_number, page_size):
     # Điều kiện để tìm các bản ghi chưa xử lý
    query = {
        "$or": [
            {"isCheck": {"$exists": False}},  # Trường 'isCheck' không tồn tại
            {"isCheck": False}                # Trường 'isCheck' tồn tại và có giá trị là False
        ]
    }
    # Tính toán số lượng bản ghi cần bỏ qua
    skip_records = page_number * page_size
    # Truy vấn các bản ghi khớp với điều kiện và áp dụng phân trang
    documents = collection.find().skip(skip_records).limit(page_size) # Danh sách bản ghi chưa xử lý lọc trùng
    return list(documents)

def  handleCheckSameTopic(document, matching_documents):
    prompt = f""
    str_document = json_util.dumps(document)
    if not document:
        return {}
    if not matching_documents or len(matching_documents) == 0:
        return {
            "isDuplicate": False,
        }
    try:
        document["_id"] = str(document["_id"])
        str_mathching_documents = json_util.dumps(matching_documents)
        prompt = f"Sản phẩm A có chi tiết như sau {str_document} có tương đồng với bất kì sản phẩm nào trong danh sách sản phẩm {str_mathching_documents}. Bạn chỉ cần trả về dữ liệu kiểu json nhưng format sang string có 2 trường là isDuplicate: True là bản ghi có tương đồng, False là không tương đồng."
        response = askGemini(prompt)
        jsondata = getJsonDataFromResGemini(response.text)
        if 'isDuplicate' in jsondata:
            return {
                "isDuplicate": jsondata['isDuplicate'],
                KEYWORDS: jsondata.get(KEYWORDS, [])
            } #trùng nhau
        else:
            return {}
        return {} #không check được
    except:
        return {}
    

def getKeywordsDocument(document): 
    if document and "title" in document:
        try:
            str_document = json_util.dumps(document)
            prompt = f"Sản phẩm A có tiêu đề như sau {document["title"]}. Các keyword của tiêu đề này là gì. Bạn chỉ cần trả cho tôi dữ liệu kiểu json có trường keywords là mảng các keyword là được"
            response = askGemini(prompt)
            jsondata = getJsonDataFromResGemini(response.text)

            return jsondata.get(KEYWORDS, [])
        except:
            return []
    return []

def checkExistTopicGetKeywords(document): 
    if document: 
        if 'title' not in document:
            # Nếu không có trường title thì xóa
            return {
                "isDuplicate": True,
            }
        if 'price' not in document:
            # Nếu không có truowngff giá thì xóa
            return {
                "isDuplicate": True, 
            }

        keywords = getKeywordsDocument(document)
        if not keywords or len(keywords) == 0:
            return {}
    
        # Xử lý bằng cách cắt chuỗi keywords và lấy các bản ghi trong cơ sở dữ liệu có từ khóa trong keywords
        keyword_list = keywords
        # Tạo biểu thức chính quy từ danh sách từ khóa
        regex_pattern = '|'.join(map(re.escape, keyword_list))

        # Tạo điều kiện tìm kiếm cho trường keywords
        keywords_condition = {KEYWORDS: {"$regex": regex_pattern, "$options": "i"}}

        # Tạo điều kiện tìm kiếm cho trường isCheck
        is_check_condition = {"isCheck": True}

         # Kết hợp cả hai điều kiện với phép AND
        query = {"$and": [keywords_condition, is_check_condition]}
        matching_documents = collection.find(query)
        documents_mathching = list(matching_documents)
        response = handleCheckSameTopic(document, documents_mathching)
        if "isDuplicate" in response:
            return {
                "isDuplicate": response.get("isDuplicate"),
                 KEYWORDS: keywords
            }
        
    return {}



def handleFilter(documents):
     # Danh sách tạm thời lưu trữ các bản ghi cần xóa
    recordIDs_to_remove = []
    if documents:
       for document in documents:
           response = checkExistTopicGetKeywords(document)
           if 'isDuplicate' in response:
                print(document["title"])
                if response['isDuplicate']:
                    print("Delete")
                    print(response)
                    recordIDs_to_remove.append(ObjectId(document['_id']))
                elif len(response.get(KEYWORDS, [])) > 0:
                    print("Update")
                    print(response)
                    collection.update_one({"_id": ObjectId(document['_id'])}, {"$set": {"isCheck": True, KEYWORDS: response.get(KEYWORDS)}})
    if recordIDs_to_remove:
        collection.delete_many({"_id": {"$in": recordIDs_to_remove}})

# page_number = 0 
# page_size = 10 
# productsNotFilter = getDocumentsNotFilter(page_number, page_size)
# handleFilter(productsNotFilter)
# while len(productsNotFilter) == page_size:
#     productsNotFilter = getDocumentsNotFilter(page_number, page_size)
#     handleFilter(productsNotFilter)

# client.close()




