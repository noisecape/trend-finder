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
        {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"},
        {"name": "link_name", "selector": "a", "type": "text"},
        {"name": "short_description", "selector": "p.text-xs.font-thin.text-gray-500", "type": "text"},
        {"name": "percentage", "selector": "div.p-2.pl-3.text-xs.md\\:text-sm.text-gray-700.font-semibold.col-span-3.sm\\:col-span-2", "type": "text"}, # Placeholder for page content
    ]
}