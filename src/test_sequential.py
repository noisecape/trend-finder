import asyncio
import json

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig
from crawl4ai.async_configs import CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
import pandas as pd

COMMUNITY_RANGE =[
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
            {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"},
            {"name": "link_name", "selector": "a", "type": "text"},
            {"name": "short_description", "selector": "p.text-xs.font-thin.text-gray-500", "type": "text"},
            {"name": "percentage", "selector": "div.p-2.pl-3.text-xs.md\\:text-sm.text-gray-700.font-semibold.col-span-3.sm\\:col-span-2", "type": "text"},
            {"name": "page_content", "selector": "", "type": "text"}  # Placeholder for page content
        ]
    }

page_schema = {
    "name": "Page Component Extraction",
    "baseSelector": "div.container.m-4",
    "fields": [
        {
            "name": "components",
            "selector": "div.p-4.relative.bg-gray-100.border.border-gray-200.shadow-lg.rounded-2xl",
            "type": "list",
            "fields": [
                {
                    "name": "value",
                    "selector": "div.text-lg.lg\\:text-2xl.text-gray-500.font-semibold.leading-8.mt-5",
                    "type": "text"
                },
                {
                    "name": "created_label",
                    "selector": "span",
                    "type": "text"
                }
            ]
        },
        {
            "name": "subscriber_growth",
            "selector": "div.h-64.p-4.relative.bg-gray-100.border.border-gray-200.shadow-lg.rounded-2xl",
            "type": "list",
            "fields": [
                {
                    "name": "period",
                    "selector": "h2.flex.justify-between.items-center.font-thin.uppercase.text-gray-400",
                    "type": "text"
                },
                {
                    "name": "day_growth",
                    "selector": "p:nth-of-type(1)::text",
                    "type": "text"
                },
                {
                    "name": "week_growth",
                    "selector": "p:nth-of-type(2)::text",
                    "type": "text"
                },
                {
                    "name": "month_growth",
                    "selector": "p:nth-of-type(3)::text",
                    "type": "text"
                }
            ]
        }
    ]
}


async def extract_page_components(url):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun_many(
            url=url,
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                extraction_strategy=JsonCssExtractionStrategy(page_schema)
            )
        )
        if result.success:
            # Parse the extracted content
            data = json.loads(result.extracted_content)
            data.append({'subreddit_link':result.links.get('external', [])[0]['href']})
            return data
        else:
            print(f"Failed to crawl {url}: {result.error_message}")
            return None

async def extract_data():
    # Define the extraction schema

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=BASE_QUERY + COMMUNITY_RANGE[0],
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                extraction_strategy=JsonCssExtractionStrategy(basepage_schema)
            )
        )
        # The JSON output is stored in 'extracted_content'
        data = json.loads(result.extracted_content)

        # Extract links from the initial data
        links = ['/'.join([BASE_DOMAIN, item['link']]) for item in data]

        # Fetch content for each link
        tasks = [extract_page_components(link) for link in links]
        page_contents = await asyncio.gather(*tasks)

        df = pd.DataFrame()

        all_records = []

        # Loop over (item, content) pairs
        for item, content in zip(data, page_contents):
            item['page_content'] = content

            # Build the data_dict from the scraped content
            data_dict = {
                'description': item['short_description'],
                "subredditName": item['page_content'][0].get("subredditName", ""),
                "subscribers": item['page_content'][1].get("subscribers", ""),
                "createdDate": item['page_content'][2].get("createdDate", ""),
                "ranking": item['page_content'][3].get("ranking", ""),
                "growthDay": item['page_content'][4].get("growthDay", ""),
                "growthWeek": item['page_content'][4].get("growthWeek", ""),
                "growthMonth": item['page_content'][4].get("growthMonth", ""),
                "growthAbsoluteDay": item['page_content'][5].get("growthAbsoluteDay", ""),
                "growthAbsoluteWeek": item['page_content'][5].get("growthAbsoluteWeek", ""),
                "growthAbsoluteMonth": item['page_content'][5].get("growthAbsoluteMonth", ""),
                "subreddit_link": item['page_content'][6].get("subreddit_link", "")
            }

            # Collect data_dict in a list
            all_records.append(data_dict)

        # Convert all_records to a DataFrame and append or assign to df
        # If df is empty, you can just create it:
        df = pd.DataFrame(all_records)  
        df.to_csv('./results.csv', index=False)



if __name__ == "__main__":
    asyncio.run(extract_data())