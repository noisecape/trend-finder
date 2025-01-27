import asyncio
import json
import re

import pandas as pd
from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig
from crawl4ai.async_configs import CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
import os

from consts import (BASE_DOMAIN, BASE_QUERY, COMMUNITY_RANGE, basepage_schema)

# Change the current working directory to the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))


async def get_pages_from_url(url:str):
     # 1) Crawl the main ranking page (single arun)
    async with AsyncWebCrawler() as crawler:
        # First crawl to get the list of items
        base_result = await crawler.arun(
            url=url,
            config=CrawlerRunConfig(
                magic=True,
                simulate_user=True,
                override_navigator=True,
                cache_mode=CacheMode.BYPASS,
                extraction_strategy=JsonCssExtractionStrategy(basepage_schema)
            )
        )

        if not base_result.success:
            print(f"Failed to crawl base page: {base_result.error_message}")
            return
        try:

            # Parse the base page items into a Python list
            data = json.loads(base_result.extracted_content)
        except Exception as e:
            print(f"Error while parsing data to json: {e}")

        # Build the full URLs for each item
        links = ['/'.join([BASE_DOMAIN, item['link']]) for item in data]
    return data, links


def parse_markdown(markdown_text):
    extracted_data = {}
    
    # Subscribers
    subscribers_match = re.search(r"Subscribers\s*\n\s*(\d+)", markdown_text)
    extracted_data["Subscribers"] = int(subscribers_match.group(1)) if subscribers_match else None

    # Created
    created_match = re.search(r"Created\s*\n\s*([^\n]+)", markdown_text)
    extracted_data["Created"] = created_match.group(1).strip() if created_match else None

    # Ranking
    ranking_match = re.search(r"Ranking\s*\n\s*(\d+)", markdown_text)
    extracted_data["Ranking"] = int(ranking_match.group(1)) if ranking_match else None

    # %-Subscriber Growth per Period
    # Match everything after "Day:" until newline, capturing the entire substring (which includes possible spaces, plus/minus signs, percentages, etc.)
    # We do the same for "Week" and "Month".
    growth_percent_pattern = re.search(
        r"%(?:-)?Subscriber Growth per Period.*?"
        r"Day:\s*([^\n]+).*?"
        r"Week:\s*([^\n]+).*?"
        r"Month:\s*([^\n]+)",
        markdown_text,
        re.DOTALL
    )
    if growth_percent_pattern:
        day_val, week_val, month_val = growth_percent_pattern.groups()
        # Clean up extra spaces
        day_val = re.sub(r"\s+", " ", day_val).strip()
        week_val = re.sub(r"\s+", " ", week_val).strip()
        month_val = re.sub(r"\s+", " ", month_val).strip()
        extracted_data["Percent Growth"] = {
            "Day": day_val,
            "Week": week_val,
            "Month": month_val
        }
    else:
        extracted_data["Percent Growth"] = None

    # Absolute Growth (e.g., "New Subscribers per Period")
    absolute_growth_pattern = re.search(
        r"New Subscribers per Period.*?"
        r"Day:\s*([^\n]+).*?"
        r"Week:\s*([^\n]+).*?"
        r"Month:\s*([^\n]+)",
        markdown_text,
        re.DOTALL
    )
    if absolute_growth_pattern:
        day_val, week_val, month_val = absolute_growth_pattern.groups()
        day_val = re.sub(r"\s+", " ", day_val).strip()
        week_val = re.sub(r"\s+", " ", week_val).strip()
        month_val = re.sub(r"\s+", " ", month_val).strip()
        extracted_data["Absolute Growth"] = {
            "Day": day_val,
            "Week": week_val,
            "Month": month_val
        }
    else:
        extracted_data["Absolute Growth"] = None

    return extracted_data


async def get_content_from_pages(page_links, data):
    # 2) Crawl each detail URL in parallel using arun_many()
    async with AsyncWebCrawler() as crawler:
        detail_results = await crawler.arun_many(
            urls=page_links,
            config=CrawlerRunConfig(
                magic=True,
                simulate_user=True, 
                override_navigator=True,
                cache_mode=CacheMode.BYPASS,
            )
        )

    # 3) Combine the base items with their corresponding page_content
    all_records = []
    for item, result in zip(data, detail_results):
        if result.success:
            # Convert extracted JSON from the detail page into Python
            try:
                page_data = parse_markdown(result.markdown)
                if result.links.get('external'):
                    page_data['subreddit_link'] = result.links['external'][0]['href']
                # Attach it so we can pick relevant fields
                item['page_content'] = page_data

                # Build the data_dict from the detail data
                data_dict = {
                    'description': item.get('short_description', ""),
                    "subredditName": item.get("link_name", ""),
                    "subscribers": page_data.get("Subscribers", ""),
                    "createdDate": page_data.get("Created", ""),
                    "ranking": page_data.get("Ranking", ""),
                    "growthDay": page_data.get("Percent Growth", "").get('Day', ''),
                    "growthWeek": page_data.get("Percent Growth", "").get('Week', ''),
                    "growthMonth": page_data.get("Percent Growth", "").get('Month', ''),
                    "growthAbsoluteDay": page_data.get("Absolute Growth", "").get('Day', ''),
                    "growthAbsoluteWeek": page_data.get("Absolute Growth", "").get('Week', ''),
                    "growthAbsoluteMonth": page_data.get("Absolute Growth", "").get('Month', ''),
                    "subreddit_link": page_data.get("subreddit_link", "")
                }
                all_records.append(data_dict)
            except Exception as e:
                print(f"Error while parsing data to json: {e}")
            # Optionally, add the first external link if you want it
        else:
            print(f"Failed to crawl {result.url}: {result.error_message}")
            page_data = [{} for _ in range(7)]  # Make sure we have enough placeholders

    return all_records

async def scrape_data(base_url:str):

    data, links = await get_pages_from_url(base_url)
    
    all_records = await get_content_from_pages(links, data)

    df = pd.DataFrame(all_records)
    df.to_csv('./data/results_1000001_100000000.csv', index=False)
    print("Scraping completed. Results saved to results.csv")

if __name__ == "__main__":
    for c_range in COMMUNITY_RANGE:
        base_url = BASE_QUERY + c_range
        filename = f"{c_range.replace('-', '_')}.csv"
        filename = '_'.join(['results', filename])
        if os.path.exists(os.path.join('data',filename)):
            continue
        base_url = BASE_QUERY + c_range
        asyncio.run(scrape_data(base_url, filename))
