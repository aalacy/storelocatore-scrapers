from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4
import asyncio
import httpx
import os
import json
import time

EXPECTED_TOTAL = 0
DEFAULT_PROXY_URL = "http://groups-RESIDENTIAL,country-us:{}@proxy.apify.com:8000/"
logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")


def set_proxies():
    if "PROXY_PASSWORD" in os.environ and os.environ["PROXY_PASSWORD"].strip():

        proxy_password = os.environ["PROXY_PASSWORD"]
        url = (
            os.environ["PROXY_URL"] if "PROXY_URL" in os.environ else DEFAULT_PROXY_URL
        )
        proxy_url = url.format(proxy_password)
        proxies = {
            "http://": proxy_url,
        }
        return proxies
    else:
        return None


proxies = set_proxies()


async def fetch_data(index: int, url: str) -> dict:
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    timeout = httpx.Timeout(60.0, connect=120.0)
    data = {}
    if len(url) > 0:
        async with httpx.AsyncClient(
            proxies=proxies, headers=headers, timeout=timeout
        ) as client:
            response = await client.get(url)
            soup = b4(response.text, "lxml")
            logzilla.info(f"URL\n{url}\nLen:{len(response.text)}\n\n")
            data = json.loads(
                str(
                    soup.find(
                        "script",
                        {"type": "application/ld+json", "id": "schema-webpage"},
                    ).text
                )
                .replace("\u0119", "e")
                .replace("\u011f", "g")
                .replace("\u0144", "n")
                .replace("\u0131", "i"),
                strict=False,
            )
            data["index"] = index
            data["requrl"] = url
            data["STATUS"] = True
    else:
        await asyncio.sleep(0)  # had to improvise
        data["index"] = index
        data["requrl"] = "<MISSING>"
        data["STATUS"] = False
    return data


async def get_brand(brand_code, brand_name, url):
    url = url + brand_code

    headers = {}
    headers["authority"] = "www.radissonhotels.com"
    headers["method"] = "GET"
    headers["path"] = "/zimba-api/destinations/hotels?brand=" + brand_code
    headers["scheme"] = "https"
    headers["accept"] = "application/json, text/plain, */*"
    headers["accept-encoding"] = "gzip, deflate, br"
    headers["accept-language"] = "en-us"
    headers["referer"] = "https://www.radissonhotels.com/en-us/destination"
    headers["sec-fetch-dest"] = "empty"
    headers["sec-fetch-mode"] = "cors"
    headers["sec-fetch-site"] = "same-origin"
    headers[
        "user-agent"
    ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"

    session = SgRequests()
    son = session.get(url, headers=headers).json()
    task_list = []
    results = []
    chunk_size = 50
    last_chunk = 0
    last_tick = time.monotonic()
    total_records = len(son["hotels"])
    global EXPECTED_TOTAL
    EXPECTED_TOTAL += total_records
    for index, record in enumerate(son["hotels"]):
        task_list.append(fetch_data(index, record["overviewPath"]))
        if index % chunk_size == 0 and last_chunk != index:
            last_tick = time.monotonic()
            last_chunk = index
            if len(task_list) > 0:
                z = await asyncio.gather(*task_list)
                for item in z:
                    results.append(
                        {
                            "main": son["hotels"][item["index"]],
                            "sub": item,
                            "@type": brand_name,
                        }
                    )
                logzilla.info(
                    f"Finished {last_chunk}/{total_records} for brand {brand_name}, last step took {round(time.monotonic()-last_tick,5)} seconds."
                )
                task_list = []

    last_tick = time.monotonic()
    if len(task_list) > 0:
        z = await asyncio.gather(*task_list)
        for item in z:
            results.append(
                {"main": son["hotels"][item["index"]], "sub": item, "@type": brand_name}
            )
        logzilla.info(
            f"Finished {total_records}/{total_records} for brand {brand_name}, last step took {round(time.monotonic()-last_tick,5)} seconds."
        )
    return results


def clean_record(k):
    try:
        k["sub"] = k["sub"]
    except Exception:
        k["sub"] = {}
        k["sub"]["mainEntity"] = {}
        k["sub"]["mainEntity"]["address"] = {}
        k["sub"]["mainEntity"]["address"]["streetAddress"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["addressLocality"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["addressRegion"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["postalCode"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["addressCountry"] = "<MISSING>"
        k["sub"]["mainEntity"]["telephone"] = ["<MISSING>"]
        k["sub"]["mainEntity"]["@type"] = "<MISSING>"

    try:
        k["sub"]["mainEntity"] = k["sub"]["mainEntity"]
    except Exception:
        k["sub"]["mainEntity"] = {}
        k["sub"]["mainEntity"]["address"] = {}
        k["sub"]["mainEntity"]["address"]["streetAddress"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["addressLocality"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["addressRegion"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["postalCode"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["addressCountry"] = "<MISSING>"
        k["sub"]["mainEntity"]["telephone"] = ["<MISSING>"]
        k["sub"]["mainEntity"]["@type"] = "<MISSING>"

    try:
        k["sub"]["mainEntity"]["address"] = k["sub"]["mainEntity"]["address"]
    except Exception:
        k["sub"]["mainEntity"]["address"] = {}
        k["sub"]["mainEntity"]["address"]["streetAddress"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["addressLocality"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["addressRegion"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["postalCode"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["addressCountry"] = "<MISSING>"

    try:
        k["sub"]["mainEntity"]["address"]["streetAddress"] = k["sub"]["mainEntity"][
            "address"
        ]["streetAddress"]
    except Exception:
        k["sub"]["mainEntity"]["address"]["streetAddress"] = "<MISSING>"

    try:
        k["sub"]["mainEntity"]["address"]["addressLocality"] = k["sub"]["mainEntity"][
            "address"
        ]["addressLocality"]
    except Exception:
        k["sub"]["mainEntity"]["address"]["addressLocality"] = "<MISSING>"

    try:
        k["sub"]["mainEntity"]["address"]["addressRegion"] = k["sub"]["mainEntity"][
            "address"
        ]["addressRegion"]
    except Exception:
        k["sub"]["mainEntity"]["address"]["addressRegion"] = "<MISSING>"

    try:
        k["sub"]["mainEntity"]["address"]["postalCode"] = k["sub"]["mainEntity"][
            "address"
        ]["postalCode"]
    except Exception:
        k["sub"]["mainEntity"]["address"]["postalCode"] = "<MISSING>"

    try:
        k["sub"]["mainEntity"]["address"]["addressCountry"] = k["sub"]["mainEntity"][
            "address"
        ]["addressCountry"]
    except Exception:
        k["sub"]["mainEntity"]["address"]["addressCountry"] = "<MISSING>"

    try:
        k["sub"]["mainEntity"]["telephone"] = k["sub"]["mainEntity"]["telephone"]
    except Exception:
        k["sub"]["mainEntity"]["telephone"] = "<MISSING>"

    try:
        k["sub"]["mainEntity"]["@type"] = k["sub"]["mainEntity"]["@type"]
    except Exception:
        k["sub"]["mainEntity"]["@type"] = ""

    try:
        k["main"] = k["main"]
    except Exception:
        k["main"] = {}
        k["main"]["coordinates"] = {}
        k["main"]["coordinates"]["latitude"] = "<MISSING>"
        k["main"]["coordinates"]["longitude"] = "<MISSING>"
        k["main"]["code"] = "<MISSING>"
        k["main"]["name"] = "<MISSING>"

    try:
        k["main"]["coordinates"] = k["main"]["coordinates"]
    except Exception:
        k["main"]["coordinates"] = {}
        k["main"]["coordinates"]["latitude"] = "<MISSING>"
        k["main"]["coordinates"]["longitude"] = "<MISSING>"

    try:
        k["main"]["code"] = k["main"]["code"]
    except Exception:
        k["main"]["code"] = "<MISSING>"

    try:
        k["main"]["name"] = k["main"]["name"]
    except Exception:
        k["main"]["name"] = "<MISSING>"

    return k


def start():
    urls = [
        "https://www.radissonhotelsamericas.com/zimba-api/destinations/hotels?brand=",
        "https://www.radissonhotels.com/zimba-api/destinations/hotels?brand=",
    ]
    brands = [
        {"code": "pii", "name": "Park Inn by Radisson"},
        {"code": "rdb", "name": "Radisson Blu"},
        {"code": "rdr", "name": "Radisson RED"},
        {"code": "art", "name": "art'otel"},
        {"code": "rad", "name": "Radisson"},
        {"code": "ri", "name": "Radisson Individuals"},
        {"code": "prz", "name": "prizeotel"},
        {"code": "pph", "name": "Park Plaza"},
        {"code": "cis", "name": "Country Inn & Suites"},
        {"code": "rco", "name": "Radisson Collection"},
    ]
    badrecords = []
    for url in urls:
        for brand in brands:
            start_time = time.monotonic()
            logzilla.info(f"Selected brand: {brand}")
            data = asyncio.run(
                get_brand(
                    brand["code"],
                    brand["name"],
                    "https://www.radissonhotels.com/zimba-api/destinations/hotels?brand=",
                )
            )
            for i in data:
                k = clean_record(i)
                if k["sub"]["STATUS"]:
                    yield k
                else:
                    badrecords.append(k)
                    yield k
            logzilla.info(
                f"Finished brand {brand['name']}, it took {round(time.monotonic()-start_time,5)}\n it has {len(data)} locations"
            )
    logzilla.info(f"Badrecords :\n\n{badrecords}")
    global EXPECTED_TOTAL
    logzilla.info(f"Finished grabbing data!!\n expected total {EXPECTED_TOTAL}")  # noqa


def scrape():
    url = "https://www.radissonhotels.com/en-us/destination"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["sub", "requrl"],
            is_required=False,
        ),
        location_name=sp.MappingField(
            mapping=["main", "name"],
            is_required=False,
        ),
        latitude=sp.MappingField(
            mapping=["main", "coordinates", "latitude"],
            is_required=False,
        ),
        longitude=sp.MappingField(
            mapping=["main", "coordinates", "longitude"],
            is_required=False,
        ),
        street_address=sp.MappingField(
            mapping=["sub", "mainEntity", "address", "streetAddress"],
            is_required=False,
        ),
        city=sp.MappingField(
            mapping=["sub", "mainEntity", "address", "addressLocality"],
            is_required=False,
        ),
        state=sp.MappingField(
            mapping=["sub", "mainEntity", "address", "addressRegion"],
            is_required=False,
        ),
        zipcode=sp.MappingField(
            mapping=["sub", "mainEntity", "address", "postalCode"], is_required=False
        ),
        country_code=sp.MappingField(
            mapping=["sub", "mainEntity", "address", "addressCountry"],
            is_required=False,
        ),
        phone=sp.MappingField(
            mapping=["sub", "mainEntity", "telephone", 0],
            is_required=False,
        ),
        store_number=sp.MappingField(
            mapping=["main", "code"],
            is_required=False,
        ),
        hours_of_operation=sp.MissingField(),
        location_type=sp.MappingField(
            mapping=["@type"],
            is_required=False,
        ),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=start,
        field_definitions=field_defs,
        log_stats_interval=30,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
