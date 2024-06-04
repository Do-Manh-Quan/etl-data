from playwright.async_api import async_playwright
from fake_useragent import UserAgent
from server.product.route import collection
import time
async def crawl_aliexpress_store(url):
    ua = UserAgent(platforms='mobile')
    user_agent = ua.random

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context(user_agent=user_agent, geolocation={"longitude": -95.7129, "latitude": 37.0902},viewport={"width": 375, "height": 667},
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True)
        

        count = 0
        page = await context.new_page()
        while True:
            await page.goto(url)
            time.sleep(5)
            previous_height = None
            while True:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(2000) 
                current_height = await page.evaluate("document.body.scrollHeight")
                if current_height == previous_height:
                    break
                previous_height = current_height
            count = count+1
            print(count)
            parent_element = await page.query_selector('//*[@id="container"]/div/div[2]/div[2]/div[2]/div[1]')
            product_elements = await parent_element.query_selector_all('>div')
            print(len(product_elements))

            if count >= len(product_elements):
                break    
                
            else:
                try:
                    await product_elements[count-1].click()
                    time.sleep(5)
                    await page.wait_for_timeout(5000) 
                    await page.wait_for_selector('div.slide')
                    curent_url = page.url
                    title_element = await page.query_selector('h1')
                    title = await title_element.evaluate('(element) => element.textContent')
                    price = ''
                    for span in await (await page.query_selector('span.dcss-price-current')).query_selector_all('span'):
                        price += await span.inner_text()
                    images_product = []
                    for image in (await page.query_selector_all('div.slide')):
                        img = await image.query_selector('img')
                        if img:
                            images_product.append(await img.get_attribute('src'))

                    skus = []
                    for s in await page.query_selector_all('div[class^="sku-ui--property"]'):
                        type =(await (await s.query_selector("//div[contains(@class, 'sku-ui--title')]")).inner_text()).split(':')[0]
                        item = []
                        for i in (await s.query_selector_all('[data-sku-col]')):
                            if await i.evaluate("el => el.tagName") == 'SPAN':
                                item.append({
                                    "label": await i.inner_text(),
                                    "value": await i.inner_text()
                                })
                            else:
                                item.append({
                                    "label": await (await i.query_selector('img')).get_attribute('alt'),
                                    "value": await (await i.query_selector('img')).get_attribute('src')
                                })
                        skus.append({
                            'type': type,
                            'item': item
                        })

                    await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(5000) 
                    await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")

                    await page.wait_for_timeout(5000)  # Wait for 3 seconds
                    reviews = []
                    rv = await page.query_selector('div[class^="reviews--rating"]')
                    if rv:
                        await rv.click()
                        await page.wait_for_timeout(5000)  # Wait for 5 seconds
                        for rv in await page.query_selector_all('div[class^="review-card--container"]'):
                            rating_overlay = await rv.query_selector('div[class^="rating--rating-overlay"]')
                            width = await rating_overlay.evaluate('(element) => element.style.width')
                            start = float(width[:-1]) / 20
                            review = await (await rv.query_selector('p[class^="review-card--feedback"]')).inner_text()
                            sku = await (await rv.query_selector('div[class^="review-card--sku"]')).inner_text()
                            images = ["https:" + (await image.get_attribute('src')) for image in await rv.query_selector_all('img[class^="review-card--thumbinail"]')]
                            reviews.append({
                                "start": start,
                                "sku": sku,
                                "review": review,
                                "images": images,
                            })
                    des = ''
                    if await page.query_selector('iframe[class^="overview--iframe"]'):
                        url_des = await (await page.query_selector('iframe[class^="overview--iframe"]')).get_attribute('src')
                        await page.goto(url=url_des)
                        await page.wait_for_selector('body')
                        des = await (await page.query_selector('body')).inner_html()
                    product = {
                        'title': title,
                        'images': images_product,
                        'price': price,
                        'sku': skus,
                        'reviews': reviews,
                        'des': des,
                        'url': curent_url,
                        'root': url
                    }
                    print(product)

                    collection.insert_one(product)
                    time.sleep(5)

                except Exception as e:
                    print('Error')

        
        await browser.close()
        
            # 
# import asyncio
# async def main():
#     url = "https://m.aliexpress.com/store/1102418174?&shopId=1102418174&sellerId=2671586218&pagePath=allProduct.htm&spm=a2g0n.store_m_home.bottom_view_more_-1717173670435.0"
#     await crawl_aliexpress_store(url)

# asyncio.run(main())