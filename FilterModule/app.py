from pymongo import MongoClient

# URI kết nối SRV (thay thế <username>, <password>, và <cluster-url> bằng thông tin của bạn)
uri = "mongodb+srv://nguyenvanlongbg2001:ka6kyzwEaSMVEnQu@cluster0.7y06ruo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Kết nối đến MongoDB Atlas
client = MongoClient(uri)

# Truy cập vào cơ sở dữ liệu
db = client['integration_data']

# Truy cập vào collection
collection = db['product']

# Lấy dữ liệu từ collection (ví dụ, tất cả các documents)
# Tạo biểu thức chính quy để tìm các documents có trường name chứa từ "Anh em"
query = {"name": {"$regex": "OK", "$options": "i"}}  # "$options": "i" để không phân biệt chữ hoa chữ thường

# Lấy dữ liệu từ collection theo truy vấn
documents = collection.find(query)

# In ra các documents
for doc in documents:
    print(doc)

# Đóng kết nối (tùy chọn, PyMongo sẽ tự động quản lý kết nối)
client.close()
