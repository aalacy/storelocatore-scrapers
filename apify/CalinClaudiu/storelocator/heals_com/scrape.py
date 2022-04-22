from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup as b4
import json

# Here some random text to change filesize so that JIRA automation will consider this for a fresh run rather than paste the same old failure log # noqa


def parse_store(k, session):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    }

    page = SgRequests.raise_on_err(
        session.get(
            k["page_url"],
            headers=headers,
        )
    )

    soup = b4(page.text, "lxml")
    try:
        data = soup.find("div", {"data-content-type": "map", "data-locations": True})[
            "data-locations"
        ]

    except Exception:
        data = None
    if data:
        data = json.loads(data)[0]
        k["address"] = data["address"]
        k["city"] = data["city"]
        k["region"] = data["state"]
        k["zip"] = data["zipcode"]
        k["phone"] = data["phone"]
        k["lat"] = data["position"]["latitude"]
        k["lon"] = data["position"]["longitude"]
        k["name"] = data["location_name"]
        k["country"] = data["country"]
        k["id"] = data["record_id"]

    try:
        h = soup.find_all("p")
        hours = []
        for div in h:
            if "day" in div.text:
                if any(
                    i in div.text
                    for i in ["open to our new", "car park", "We are proud"]
                ):
                    continue
                hours.append(div.text)
        hours.pop(-1)
        k["hours"] = "; ".join(hours)
    except Exception:
        k["hours"] = "<MISSING>"

    return k


def fetch_data():

    logzilla = sglog.SgLogSetup().get_logger(logger_name="CRAWLER")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    }

    with SgRequests() as session:
        url = "https://www.heals.com/stores"
        page = session.get(url, headers=headers)
        soup = b4(page.text, "lxml")
        results = []
        locs = soup.find(
            "ul",
            {"class": lambda x: x and all(i in x for i in ["dropdown", "stores"])},
        ).find_all("li")
        for i in locs:
            k = {}
            k["page_url"] = "https://www.heals.com/" + i.find("a")["href"]
            if k["page_url"].count("/") >= 5:
                results.append(k)
        for i in results:
            yield parse_store(i, session)

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    x = x.replace("None", "")
    h = []
    try:
        x = x.split(",")
        for i in x:
            st = i.strip()
            if len(st) >= 1:
                h.append(st)
        h = ", ".join(h)
    except Exception:
        h = x

    return h


def fix_colon(x):
    x = x.replace("None", "")
    h = []
    try:
        x = x.split(":")
        for i in x:
            st = i.strip()
            if len(st) >= 1:
                h.append(st)
        h = ", ".join(h)
    except Exception:
        h = x

    return h


def scrape():
    url = "https://www.heals.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["page_url"],
            is_required=False,
        ),
        location_name=sp.MappingField(
            mapping=["name"],
            is_required=False,
        ),
        latitude=sp.MappingField(
            mapping=["lat"], is_required=False, part_of_record_identity=True
        ),
        longitude=sp.MappingField(
            mapping=["lon"], is_required=False, part_of_record_identity=True
        ),
        street_address=sp.MappingField(
            mapping=["address"],
            is_required=False,
        ),
        city=sp.MappingField(
            mapping=["city"],
            is_required=False,
        ),
        state=sp.MappingField(
            mapping=["region"],
            is_required=False,
        ),
        zipcode=sp.MappingField(
            mapping=["zip"], is_required=False, part_of_record_identity=True
        ),
        country_code=sp.MappingField(
            mapping=["country"],
            is_required=False,
        ),
        phone=sp.MappingField(
            mapping=["phone"], is_required=False, part_of_record_identity=True
        ),
        store_number=sp.MappingField(mapping=["id"], part_of_record_identity=True),
        hours_of_operation=sp.MappingField(
            mapping=["hours"],
            value_transform=lambda x: x.replace("/", ":"),
            is_required=False,
        ),
        location_type=sp.MissingField(),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
