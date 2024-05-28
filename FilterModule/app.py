import os
from pymongo import MongoClient
import google.generativeai as genai
from bson import json_util
from bson import ObjectId
import re
# URI kết nối SRV (thay thế <username>, <password>, và <cluster-url> bằng thông tin của bạn)
uri = "mongodb+srv://nguyenvanlongbg2001:ka6kyzwEaSMVEnQu@cluster0.7y06ruo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Kết nối đến MongoDB Atlas
client = MongoClient(uri)

# Truy cập vào cơ sở dữ liệu
db = client['integration_data']

# Truy cập vào collection
collection = db['product']

genai.configure(api_key="AIzaSyAKWIqNFsMYTkcnvbWU8KTUosuGBib79R4")
# The Gemini 1.5 models are versatile and work with both text-only and multimodal prompts
model = genai.GenerativeModel('gemini-1.5-flash')
schema = ""
def askGemini(prompt):
    if prompt:
      response = model.generate_content(prompt)
      return response
    return ""


def getDocumentsNotFilter(page_number, page_size):
     # Điều kiện để tìm các bản ghi chưa xử lý
    query = {"isCheck": "False" }
    # Tính toán số lượng bản ghi cần bỏ qua
    skip_records = page_number * page_size
    # Truy vấn các bản ghi khớp với điều kiện và áp dụng phân trang
    documents = collection.find(query).skip(skip_records).limit(page_size) # Danh sách bản ghi chưa xử lý lọc trùng
    return list(documents)

def  checkSameTopic(document, matching_documents):
    if not document or not matching_documents:
        return -1
    document["_id"] = str(document["_id"])
    str_document = json_util.dumps(document)
    str_mathching_documents = json_util.dumps(matching_documents)
    prompt = f"Sản phẩm có chi tiết như sau {str_document} có tương đồng với bất kì sản phẩm nào trong danh sách sản phẩm {str_mathching_documents}. Nếu có tương đồng bạn chỉ cần trả lời là 1, nếu không bạn chỉ cần trả lời là 0."
    response = askGemini(prompt)
    if response.text.strip() == "1":
        return 1 #trùng nhau
    elif response.text.strip() == "0":
        return 0 # không trùng
    return -1 #không check được

def checkIsExistTopic(document): 
    if document: 
        if 'keywords' not in document:
            print("Document không có trường keywords.")
            return -1

        keywords = document['keywords']
        if not keywords:
            print("Document không có keywords.")
            return -1
    
        # Xử lý bằng cách cắt chuỗi keywords và lấy các bản ghi trong cơ sở dữ liệu có từ khóa trong keywords
        keyword_list = keywords.split(',')
        # Tạo biểu thức chính quy từ danh sách từ khóa
        regex_pattern = '|'.join(map(re.escape, keyword_list))

        # Tạo điều kiện tìm kiếm cho trường keywords
        keywords_condition = {"keywords": {"$regex": regex_pattern, "$options": "i"}}

        # Tạo điều kiện tìm kiếm cho trường isCheck
        is_check_condition = {"isCheck": "True"}

         # Kết hợp cả hai điều kiện với phép AND
        query = {"$and": [keywords_condition, is_check_condition]}
        matching_documents = collection.find(query)
        if matching_documents:
            isSameTopic = checkSameTopic(document, matching_documents)
            return isSameTopic
    return -1



def handleFilter(documents):
     # Danh sách tạm thời lưu trữ các bản ghi cần xóa
    records_to_remove = []
    records_to_update_status = []
    if documents:
       for document in documents:
           status = checkIsExistTopic(document)
           if status == 1:
               records_to_remove.append(ObjectId(document['_id'])) # Danh sách bản ghi trùng nên xóa
           elif status == 0:
               records_to_update_status.append(ObjectId(document['_id'])) # Danh sách ben ghi không bị trùng nên cập nhật trạng thái
                
    if records_to_remove:
        collection.delete_many({"_id": {"$in": records_to_remove}})
    if records_to_update_status:
        collection.update_many({"_id": {"$in": records_to_update_status}}, {"$set": {"isCheck": "True"}})
    
    
page_number = 0
page_size = 10
productsNotFilter = getDocumentsNotFilter(page_number, page_size)
handleFilter(productsNotFilter)


# Đóng kết nối (tùy chọn, PyMongo sẽ tự động quản lý kết nối)
client.close()




