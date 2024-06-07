from playwright.async_api import async_playwright
from fake_useragent import UserAgent
import json
from typing import List
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
import asyncio
from bs4 import BeautifulSoup
from server.product.route import collection




def extract_json(message: AIMessage) -> List[dict]:
    text = message.content
    try:
        cleaned_json_str = text.replace("```json", "").replace("```", "").replace("'", '"')
        print(cleaned_json_str)
        
        data = json.loads(cleaned_json_str)
        
        return data
    except Exception as e:
        print(f"Failed to parse JSON: {e}")
        return []


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Answer the user query. Output your answer as JSON that  "
            """Đây là schema của sản phẩm
                class Review(BaseModel):
                    start: float = Field(..., ge=0, le=5)
                    sku: str = Field(...)
                    review: str = Field(...)
                    images: List[str] = Field(...)

                class SKUItem(BaseModel):
                    label: str = Field(...)
                    value: str = Field(...)

                class SKU(BaseModel):
                    type: str = Field(...)
                    item: List[SKUItem]

                class AliexpressProductSchema(BaseModel):
                    title: str = Field(...)
                    images: List[str] = Field(...)
                    price: str = Field(...)
                    sku: List[SKU] = Field(...)
                    reviews: List[Review] = Field(...)
                    des: str = Field(...)
            """
            "matches the given schema: ```json\n{schema}\n```. thiếu trường price và des thì tự điền vào cho phù hợp"
            "Make sure to wrap the answer in ```json and ``` tags"
            "Đây là text tách từ html của trang web một sản phẩm hãy lấy các thông tin title, images, price, sku, reviews, des nếu không có sản phẩm hãy trả về mảng rỗng"
        ),
        ("human", "{query}"),
    ]
).partial(schema=[{
    "title": "type is string không được chứa dấu ''",
    "price": "giá của sản phẩm, trường này bắt buộc phải có",
    "images": "mảng chứa danh sách string url hình ảnh của sản phẩm, nếu url hình ảnh chưa có https ở đầu thì hãy thêm URL Page vào đầu",
    "sku": "sku của sản phẩm có cấu trúc như schema sản phẩm kiểu này type: Color item: gồm label và value",
    "reviews": "đánh giá của sản phẩm có cấu trúc như schema sản phẩm, hãy tạo ra vài reviews cho sản phẩm 5 sao nếu không có reviews cho sản phẩm này",
    "des": "mô tả của sản phẩm không được chứa dấu '' và là string html"
  }])

# Initialize the ChatGoogleGenerativeAI model
llm = ChatGoogleGenerativeAI(model="gemini-pro", convert_system_message_to_human=True, temperature=0, top_p=0.85, google_api_key="AIzaSyDhIZI0YZOuVoMT64Z2By0j-U3nTSQtA28")

def extract(content:str):
    chain = prompt | llm | extract_json
    return chain.invoke({"query": content})
def scrape_with_playwright(text):
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=3000, chunk_overlap=0
    )
    splits = splitter.create_documents([text])
    return extract(content=splits[0].page_content)

async def crawl_google_store(url):
    ua = UserAgent(platforms='mobile')
    user_agent = ua.random

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=user_agent, geolocation={"longitude": -95.7129, "latitude": 37.0902},viewport={"width": 375, "height": 667})
        page = await context.new_page()
        await page.goto(url)

        seen_links = set()
        previous_height = None
        count = 0
        while True:
            count = count + 1
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)  # Wait for 2 seconds
            product_elements = await page.query_selector_all('div.sh-pr__secondary-container')
            for product in product_elements:
                link = await (await product.query_selector('a')).get_attribute('href')
                if link and link not in seen_links:
                    seen_links.add("https://google.com" +link)
            current_height = await page.evaluate("document.body.scrollHeight")
            if len(seen_links) > 100 or count > 10:
                break
            previous_height = current_height

        for linkk in seen_links:
            try:
                await page.goto(linkk)
                await page.wait_for_timeout(5000)
                await page.query_selector('div')
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(2000)
              
                soup = BeautifulSoup(await page.content(), 'html.parser')
                for img in soup.find_all('img'):
                    img.replace_with(f'Image: {img.get("src")}')
                for script_or_style in soup(['script', 'style', 'noscript']):
                    script_or_style.decompose() 
                
                text = "URL Page: " +page.url+'\n'+ soup.get_text(separator='\n', strip=True)
                print(text)
                pr = scrape_with_playwright(text)
                pr = pr[0]
                print(pr)
                if pr.get("title") and pr.get('price'):
                    product = {
                        'title':  pr.get("title"),
                        'images':  pr.get("images"),
                        'price':  pr.get("price"),
                        'sku':  pr.get("sku"),
                        'reviews':  pr.get("reviews"),
                        'des':  pr.get("des"),
                        'url': page.url,
                        'root': url
                    }
                    collection.insert_one(product)
            except Exception as e:
                print('Error', e)
