from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MissingField
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup as b4


def process_data(data):
    k = {}

    k["url"] = "https://www.bunulu.com/BUNstorelocator"

    try:
        addr = data.find("p").text
    except Exception:
        addr = "<MISSING>"
    try:
        k["store"] = data.find("h4").text
    except Exception:
        k["store"] = "<MISSING>"

    try:
        k["lat"] = data.find(
            "a",
            {
                "href": lambda x: x and x.startswith("https://www.google.com/maps/")
            },  # noqa
        )["href"]
    except Exception:
        k["lat"] = "<MISSING>"

    try:
        k["lng"] = k["lat"].split("@", 1)[1].split(",", 2)[1]
        k["lat"] = k["lat"].split("@", 1)[1].split(",", 2)[0]
    except Exception:
        k["lng"] = "<MISSING>"

    try:
        k["address"] = addr.split(",")[:-2]
        try:
            k["address"] = ",".join(k["address"])
        except Exception:
            pass
    except Exception:
        k["address"] = "<MISSING>"

    try:
        k["city"] = addr.split(",")[-2]
    except Exception:
        k["city"] = "<MISSING>"

    try:
        k["state"] = addr.split(",")[-1].strip()
        k["state"] = k["state"].split(" ")[0]
    except Exception:
        k["state"] = "<MISSING>"

    try:
        k["zip"] = addr.split(",")[-1].strip()
        k["zip"] = k["zip"].split(" ")[1]
    except Exception:
        k["zip"] = "<MISSING>"

    k["country"] = "<MISSING>"

    try:
        k["phone"] = (
            data.find("div", {"class": "contact"})
            .find("p")
            .text.replace("&nbsp", "")
            .strip()
        )
    except Exception:
        k["phone"] = "<MISSING>"

    k["id"] = "<MISSING>"

    try:
        k["hours"] = data.find("div", {"class": "hours"}).find_all(
            "time", {"datetime": True}
        )
        h = []
        for i in k["hours"]:
            h.append(i["datetime"])
        k["hours"] = "; ".join(h)

    except Exception:
        k["hours"] = "<MISSING>"

    return k


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://www.bunulu.com/BUNstorelocator"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"  # noqa
    }

    session = SgRequests()

    soup = session.get(url, headers=headers)
    soup = b4(soup.text, "lxml")
    stores = soup.find("div", {"id": "MOBILE"}).find_all(
        "div", {"class": "location"}
    )  # noqa

    for i in stores:
        yield process_data(i)

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    h = []

    x = x.replace("None", "")
    try:
        x = x.split(",")
        for i in x:
            if len(i) > 1:
                h.append(i)
        h = ", ".join(h)
    except Exception:
        h = x

    if len(h) < 2:
        h = "<MISSING>"

    return h


def scrape():
    url = "https://www.bunulu.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=["url"], is_required=False),
        location_name=MappingField(
            mapping=["store"], value_transform=lambda x: x.replace("None", "<MISSING>")
        ),
        latitude=MappingField(mapping=["lat"]),
        longitude=MappingField(mapping=["lng"]),
        street_address=MappingField(mapping=["address"], value_transform=fix_comma),
        city=MappingField(
            mapping=["city"], value_transform=lambda x: x.replace("None", "<MISSING>")
        ),
        state=MappingField(
            mapping=["state"], value_transform=lambda x: x.replace("None", "<MISSING>")
        ),
        zipcode=MappingField(
            mapping=["zip"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        country_code=MappingField(mapping=["country"]),
        phone=MappingField(
            mapping=["phone"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        store_number=MappingField(mapping=["id"]),
        hours_of_operation=MappingField(mapping=["hours"], is_required=False),
        location_type=MissingField(),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="bunulu.com",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
