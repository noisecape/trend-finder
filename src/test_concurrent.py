import asyncio
import json
import pandas as pd

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig
from crawl4ai.async_configs import CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

COMMUNITY_RANGE = [
    '0-100',
    '101-1000',
    '1001-10000',
    '10001-50000',
    '50001-100000',
    '100001-1000000',
    '1000001-100000000'
]

BASE_QUERY = 'https://reddstats.com/ranking/relative?over18=False&period=monthly&subscriber_classification='
BASE_DOMAIN = 'https://reddstats.com'

basepage_schema = {
    "name": "Item Extraction",
    "baseSelector": "div.item",
    "fields": [
        {
            "name": "link",
            "selector": "a",
            "type": "attribute",
            "attribute": "href"
        },
        {
            "name": "link_name",
            "selector": "a",
            "type": "text"
        },
        {
            "name": "short_description",
            "selector": "p.text-xs.font-thin.text-gray-500",
            "type": "text"
        },
        {
            "name": "percentage",
            "selector": "div.p-2.pl-3.text-xs.md\\:text-sm.text-gray-700.font-semibold.col-span-3.sm\\:col-span-2",
            "type": "text"
        },
        {
            "name": "page_content",
            "selector": "",
            "type": "text"
        }
    ]
}

page_schema = {
    "name": "Page Component Extraction",
    "baseSelector": "div.bg-gray-100.border.border-gray-200.shadow-lg.rounded-2xl",
    "fields": [
        {
            "name": "subredditName",
            "selector": "div.w-full.flex-none.text-xl.text-gray-600.font-bold.leading-none",
            "type": "text"
        },
        {
            "name": "subscribers",
            "selector": "div.text-lg.lg\\:text-2xl.text-gray-500.font-semibold.leading-8.mt-5",
            "type": "text",
            "index": 0
        },
        {
            "name": "createdDate",
            "selector": "div.text-lg.lg\\:text-2xl.text-gray-500.font-semibold.leading-8.mt-5",
            "type": "text",
            "index": 1
        },
        {
            "name": "ranking",
            "selector": "div.text-lg.lg\\:text-2xl.text-gray-500.font-semibold.leading-8.mt-5",
            "type": "text",
            "index": 2
        },
        {
            "name": "subredditLink",
            "selector": "a[href*='reddit.com/r/']",
            "type": "attribute",
            "attrName": "href"
        },
        {
            "name": "growthDay",
            "selector": "div.h-64:nth-of-type(1) p:nth-of-type(1)",
            "type": "text"
        },
        {
            "name": "growthWeek",
            "selector": "div.h-64:nth-of-type(1) p:nth-of-type(2)",
            "type": "text"
        },
        {
            "name": "growthMonth",
            "selector": "div.h-64:nth-of-type(1) p:nth-of-type(3)",
            "type": "text"
        },
        {
            "name": "growthAbsoluteDay",
            "selector": "div.h-64:nth-of-type(2) p:nth-of-type(1)",
            "type": "text"
        },
        {
            "name": "growthAbsoluteWeek",
            "selector": "div.h-64:nth-of-type(2) p:nth-of-type(2)",
            "type": "text"
        },
        {
            "name": "growthAbsoluteMonth",
            "selector": "div.h-64:nth-of-type(2) p:nth-of-type(3)",
            "type": "text"
        }
    ]
}

async def extract_data():
    # 1) Crawl the main ranking page (single arun)
    async with AsyncWebCrawler() as crawler:
        # First crawl to get the list of items
        base_result = await crawler.arun(
            url=BASE_QUERY + COMMUNITY_RANGE[0],
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                extraction_strategy=JsonCssExtractionStrategy(basepage_schema)
            )
        )

        if not base_result.success:
            print(f"Failed to crawl base page: {base_result.error_message}")
            return

        # Parse the base page items into a Python list
        data = json.loads(base_result.extracted_content)

        # Build the full URLs for each item
        links = [f"{BASE_DOMAIN}/{item['link'].lstrip('/')}" for item in data]

    # 2) Crawl each detail URL in parallel using arun_many()
    async with AsyncWebCrawler() as crawler:
        detail_results = await crawler.arun_many(
            urls=links,
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                extraction_strategy=JsonCssExtractionStrategy(page_schema)
            )
        )

    # 3) Combine the base items with their corresponding page_content
    all_records = []
    for item, result in zip(data, detail_results):
        if result.success:
            # Convert extracted JSON from the detail page into Python
            page_data = json.loads(result.extracted_content)
            # Optionally, add the first external link if you want it
            if result.links.get('external'):
                page_data.append({'subreddit_link': result.links['external'][0]['href']})
        else:
            print(f"Failed to crawl {result.url}: {result.error_message}")
            page_data = [{} for _ in range(7)]  # Make sure we have enough placeholders

        # Attach it so we can pick relevant fields
        item['page_content'] = page_data

        # Build the data_dict from the detail data
        data_dict = {
            'description': item.get('short_description', ""),
            "subredditName": page_data[0].get("subredditName", ""),
            "subscribers": page_data[1].get("subscribers", ""),
            "createdDate": page_data[2].get("createdDate", ""),
            "ranking": page_data[3].get("ranking", ""),
            "growthDay": page_data[4].get("growthDay", ""),
            "growthWeek": page_data[4].get("growthWeek", ""),
            "growthMonth": page_data[4].get("growthMonth", ""),
            "growthAbsoluteDay": page_data[5].get("growthAbsoluteDay", ""),
            "growthAbsoluteWeek": page_data[5].get("growthAbsoluteWeek", ""),
            "growthAbsoluteMonth": page_data[5].get("growthAbsoluteMonth", ""),
            "subreddit_link": page_data[6].get("subreddit_link", "")
        }
        all_records.append(data_dict)

    # 4) Create a pandas DataFrame
    df = pd.DataFrame(all_records)
    df.to_csv('./results.csv', index=False)
    print("Scraping completed. Results saved to results.csv")

if __name__ == "__main__":
    asyncio.run(extract_data())
