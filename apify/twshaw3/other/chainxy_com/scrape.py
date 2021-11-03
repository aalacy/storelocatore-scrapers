import csv
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup
from lxml import etree
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt

logger = SgLogSetup().get_logger("chainxy_com")

MISSING = "<MISSING>"


UNITED_STATES = "united-states"
UNITED_KINGDOM = "united-kingdom"
CANADA = "canada"
UK_IRELAND = "uk-ireland"
WORLDWIDE = "worldwide"

BASE_URL = "https://chainxy.com/product-categories/countries"


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "name",
                "website",
                "chain_url",
                "parent_chain_name",
                "parent_chain_url",
                "last_updated",
                "uk_ireland_count",
                "us_count",
                "ca_count",
                "worldwide_count",
                "naics_code",
                "sic_code",
                "naics_description",
                "sic_description",
                "primary",
                "secondary",
                "location_count",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Method": "GET",
    "Authority": "chainxy.com",
    "Path": "/product-categories/countries/united-kingdom/page/8/",
    "Scheme": "https",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Referrer": "https://chainxy.com/product-categories/countries/united-kingdom/",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
}


def scrape_page_url(page_url):
    logger.info(f"Fetching chain URLs from {page_url}")
    with SgRequests() as session:
        res = session.get(page_url, headers=HEADERS)
        if res.status_code // 100 == 4:
            return None
        dom = etree.HTML(res.text)
        chain_urls = dom.xpath('//span[@class="product-title"]/a/@href')
        return chain_urls


def parse_name(dom):
    title = dom.xpath('//div[contains(@class, "fusion-title")]/h1/text()')[0]
    return title.strip()


def parse_counts(dom):
    uk_ireland_count = MISSING
    us_count = MISSING
    ca_count = MISSING
    worldwide_count = MISSING
    variations_form = json.loads(
        dom.xpath(
            '//form[contains(@class, "variations_form")]/@data-product_variations'
        )[0]
    )
    if variations_form:
        for country in [UNITED_STATES, CANADA, UK_IRELAND, WORLDWIDE]:
            data = [
                x
                for x in variations_form
                if x["attributes"]["attribute_pa_country"] == country
            ]
            if data:
                description = data[0]["variation_description"]
                description_dom = etree.HTML(description)
                count = description_dom.xpath("//p/strong[3]/text()")[0]
                if country == UNITED_STATES:
                    us_count = count
                elif country == CANADA:
                    ca_count = count
                elif country == UK_IRELAND:
                    uk_ireland_count = count
                elif country == WORLDWIDE:
                    worldwide_count = count
    return uk_ireland_count, us_count, ca_count, worldwide_count


def parse_fields(dom):
    last_updated = MISSING
    website = MISSING
    location_count = MISSING
    primary = MISSING
    secondary = MISSING
    sic_code = MISSING
    sic_description = MISSING
    naics_code = MISSING
    naics_description = MISSING
    parent_chain_name = MISSING
    parent_chain_url = MISSING
    fields = dom.xpath('//div[@class="content-container"]//text()')
    fields = [field.strip() for field in fields if field.strip()]
    i = 0
    while i < len(fields):
        field = fields[i]
        if field == "Last Updated:":
            last_updated = fields[i + 1]
        elif field == "Website:":
            website = fields[i + 1]
        elif field == "Parent Chain:":
            parent_chain_name = fields[i + 1]
            parent_chain_url = dom.xpath(f'//a[text()="{parent_chain_name}"]/@href')[0]
        elif field == "Location Count:":
            location_count = fields[i + 1]
        elif field == "Primary:":
            primary = fields[i + 1]
        elif field == "Secondary:":
            secondary = fields[i + 1]
        elif field == "SIC Code:":
            sic = fields[i + 1].split("/")
            sic_code = sic[0].strip()
            sic_description = sic[1].strip()
        elif field == "NAICS Code:":
            naics = fields[i + 1].split("/")
            naics_code = naics[0].strip()
            naics_description = naics[1].strip()
        i += 1
    return (
        last_updated,
        website,
        parent_chain_name,
        parent_chain_url,
        location_count,
        primary,
        secondary,
        sic_code,
        sic_description,
        naics_code,
        naics_description,
    )


@retry(stop=stop_after_attempt(7))
def scrape_chain(chain_url):
    logger.info(f"Scraping chain {chain_url}")
    with SgRequests() as session:
        res = session.get(chain_url, headers=HEADERS)
        dom = etree.HTML(res.text)

        uk_ireland_count, us_count, ca_count, worldwide_count = parse_counts(dom)
        (
            last_updated,
            website,
            parent_chain_name,
            parent_chain_url,
            location_count,
            primary,
            secondary,
            sic_code,
            sic_description,
            naics_code,
            naics_description,
        ) = parse_fields(dom)
        name = parse_name(dom)
        record = [
            name,
            website,
            chain_url,
            parent_chain_name,
            parent_chain_url,
            last_updated,
            uk_ireland_count,
            us_count,
            ca_count,
            worldwide_count,
            naics_code,
            sic_code,
            naics_description,
            sic_description,
            primary,
            secondary,
            location_count,
        ]
        return record


def fetch_urls_for_country(country, limit=None):
    logger.info(f"Fetching chain URLs for {country}")
    country_url = f"{BASE_URL}/{country}"
    page = 1
    while limit is None or page <= limit:
        page_url = f"{country_url}/page/{page}"
        links = scrape_page_url(page_url)
        if not links:
            break
        page += 1
        yield from links


def fetch_data():
    logger.info("Starting scrape")
    chain_urls = list(fetch_urls_for_country(UNITED_STATES))
    logger.info(f"Found {len(chain_urls)} chain URLs")
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(scrape_chain, chain_url) for chain_url in chain_urls]
        for result in as_completed(futures):
            yield result.result()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
