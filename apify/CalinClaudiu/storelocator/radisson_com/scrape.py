from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog
from bs4 import BeautifulSoup as b4
from sgrequests.sgrequests import SgRequests
import json
import time
from sgscrape.pause_resume import CrawlStateSingleton

EXPECTED_TOTAL = 0
logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")


def get_main(url, headers, session):
    response = session.get(url, headers=headers)
    return response.json()


def no_json(soup):
    soup = b4(soup, "lxml")
    k = {}
    k["mainEntity"] = {}
    k["mainEntity"]["address"] = {}
    try:
        address = soup.find(
            "span",
            {"class": lambda x: x and all(i in x for i in ["item-info", "t-address"])},
        ).text.strip()
    except Exception:
        address = "<MISSING>"

    try:
        telephone = soup.find(
            "span",
            {"class": lambda x: x and all(i in x for i in ["item-info", "t-phone"])},
        ).text.strip()
    except Exception:
        telephone = "<MISSING>"

    try:
        city = soup.find("span", {"class": "t-city"})
    except Exception:
        city = "<MISSING>"

    try:
        state = soup.find("span", {"class": "t-state"})
    except Exception:
        state = "<MISSING>"

    try:
        zipcode = soup.find("span", {"class": "t-zip"})
    except Exception:
        zipcode = "<MISSING>"

    try:
        country = soup.find("span", {"class": "t-country"})
    except Exception:
        country = "<MISSING>"

    k["mainEntity"]["address"]["streetAddress"] = address
    k["mainEntity"]["address"]["telephone"] = []
    k["mainEntity"]["address"]["telephone"].append(telephone)
    k["mainEntity"]["address"]["addressLocality"] = city
    k["mainEntity"]["address"]["addressRegion"] = state
    k["mainEntity"]["address"]["postalCode"] = zipcode
    k["mainEntity"]["address"]["addressCountry"] = country
    return k


def fetch_data(index: int, url: str, headers, session) -> dict:
    data = {}
    if len(url) > 0:
        try:
            response = session.get(url, headers=headers)
            soup = b4(response.text, "lxml")
            logzilla.info(f"URL\n{url}\nLen:{len(response.text)}\n")
            if len(response.text) < 400:
                logzilla.info(f"Content\n{response.text}\n\n")
        except Exception as e:
            logzilla.error(f"err\n{str(e)}\nUrl:{url}\n\n")

        try:
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
        except Exception:
            try:
                data = no_json(response.text)
            except Exception:
                data = {}
        data["index"] = index
        data["requrl"] = url
        data["STATUS"] = True
    else:
        data["index"] = index
        data["requrl"] = "<MISSING>"
        data["STATUS"] = False
    return data


def get_brand(brand_code, brand_name, url, url2, session):

    headers = {}
    headers["authority"] = str(url).replace("https://", "")
    headers["method"] = "GET"
    headers["path"] = "/zimba-api/destinations/hotels?brand=" + brand_code
    headers["scheme"] = "https"
    headers["accept"] = "application/json, text/plain, */*"
    headers["accept-encoding"] = "gzip, deflate, br"
    headers["accept-language"] = "en-us"
    headers["referer"] = str("{}/en-us/destination").format(url)
    headers["sec-fetch-dest"] = "empty"
    headers["sec-fetch-mode"] = "cors"
    headers["sec-fetch-site"] = "same-origin"
    headers[
        "user-agent"
    ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"

    son = get_main(str(url + url2 + brand_code), headers, session)
    results = []
    total_records = len(son["hotels"])
    global EXPECTED_TOTAL
    EXPECTED_TOTAL += total_records
    for index, record in enumerate(son["hotels"]):
        z = fetch_data(index, record["overviewPath"], headers, session)
        results.append(
            {
                "main": son["hotels"][z["index"]],
                "sub": z,
                "@type": brand_name,
            }
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
    state = CrawlStateSingleton.get_instance()
    urlA = "https://www.radissonhotelsamericas.com"
    urlB = "https://www.radissonhotels.com"
    url2 = "/zimba-api/destinations/hotels?brand="
    brandsA = state.get_misc_value(
        "brandsA",
        default_factory=lambda: [
            {"code": "pii", "name": "Park Inn by Radisson", "done": False},
            {"code": "rdb", "name": "Radisson Blu", "done": False},
            {"code": "rdr", "name": "Radisson RED", "done": False},
            {"code": "art", "name": "art'otel", "done": False},
            {"code": "rad", "name": "Radisson", "done": False},
            {"code": "ri", "name": "Radisson Individuals", "done": False},
            {"code": "prz", "name": "prizeotel", "done": False},
            {"code": "pph", "name": "Park Plaza", "done": False},
            {"code": "cis", "name": "Country Inn & Suites", "done": False},
            {"code": "rco", "name": "Radisson Collection", "done": False},
        ],
    )
    brandsB = state.get_misc_value(
        "brandsB",
        default_factory=lambda: [
            {"code": "pii", "name": "Park Inn by Radisson", "done": False},
            {"code": "rdb", "name": "Radisson Blu", "done": False},
            {"code": "rdr", "name": "Radisson RED", "done": False},
            {"code": "art", "name": "art'otel", "done": False},
            {"code": "rad", "name": "Radisson", "done": False},
            {"code": "ri", "name": "Radisson Individuals", "done": False},
            {"code": "prz", "name": "prizeotel", "done": False},
            {"code": "pph", "name": "Park Plaza", "done": False},
            {"code": "cis", "name": "Country Inn & Suites", "done": False},
            {"code": "rco", "name": "Radisson Collection", "done": False},
        ],
    )
    badrecords = []
    with SgRequests() as session:
        for url in [urlA, urlB]:
            if url == urlA:
                for brand in brandsA:
                    if not brand["done"]:
                        start_time = time.monotonic()
                        logzilla.info(f"Selected brand: {brand}")
                        data = get_brand(
                            brand["code"],
                            brand["name"],
                            url,
                            url2,
                            session,
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
                        brand["done"] = True
                        state.set_misc_value("brandsA", brandsA)
            if url == urlB:
                for brand in brandsB:
                    if not brand["done"]:
                        start_time = time.monotonic()
                        logzilla.info(f"Selected brand: {brand}")
                        data = get_brand(
                            brand["code"],
                            brand["name"],
                            url,
                            url2,
                            session,
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
                        brand["done"] = True
                        state.set_misc_value("brandsB", brandsB)

    logzilla.info(f"Badrecords :\n\n{badrecords}")
    global EXPECTED_TOTAL
    logzilla.info(f"Finished grabbing data!!\n expected total {EXPECTED_TOTAL}")  # noqa


def fix_phone(x):
    if len(x) < 3:
        return "<MISSING>"
    return x


def scrape():
    url = "https://www.radissonhotels.com/en-us/destination"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["sub", "requrl"],
            is_required=False,
            part_of_record_identity=True,
        ),
        location_name=sp.MappingField(
            mapping=["main", "name"],
            is_required=False,
            part_of_record_identity=True,
        ),
        latitude=sp.MappingField(
            mapping=["main", "coordinates", "latitude"],
            is_required=False,
            part_of_record_identity=True,
        ),
        longitude=sp.MappingField(
            mapping=["main", "coordinates", "longitude"],
            is_required=False,
        ),
        street_address=sp.MappingField(
            mapping=["sub", "mainEntity", "address", "streetAddress"],
            is_required=False,
            part_of_record_identity=True,
        ),
        city=sp.MappingField(
            mapping=["sub", "mainEntity", "address", "addressLocality"],
            is_required=False,
        ),
        state=sp.MappingField(
            mapping=["sub", "mainEntity", "address", "addressRegion"],
            is_required=False,
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        zipcode=sp.MappingField(
            mapping=["sub", "mainEntity", "address", "postalCode"],
            is_required=False,
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        country_code=sp.MappingField(
            mapping=["sub", "mainEntity", "address", "addressCountry"],
            is_required=False,
        ),
        phone=sp.MappingField(
            mapping=["sub", "mainEntity", "telephone", 0],
            is_required=False,
            value_transform=fix_phone,
        ),
        store_number=sp.MappingField(
            mapping=["main", "code"],
            is_required=False,
            part_of_record_identity=True,
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
