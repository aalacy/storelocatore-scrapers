from sgscrape import simple_scraper_pipeline as sp
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup as b4
import json


def para(k):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
    }
    session = SgRequests()

    url = k["link"]
    son = session.get(url, headers=headers)
    soup = b4(son.text, "lxml")
    h = []
    for i in soup.find_all(
        "div",
        {
            "class": lambda x: x
            and all(
                lass in x
                for lass in [
                    "c-find-us__col",
                    "t-paragraph--epsilon",
                    "o-layout__item--1/2@desk-large",
                ]
            )
        },
    ):
        try:
            test = i.find("span", {"class": "c-find-us__time"})  # noqa
            h = list(i.stripped_strings)
        except Exception:
            continue
    k["hours"] = " ".join(h)

    try:
        k["latitude"] = (
            soup.find(
                "a",
                {
                    "href": lambda x: x
                    and x.startswith("https://www.google.com/maps/dir/")
                },
            )["href"]
            .split("@")[1]
            .split("/")[0]
        )
        k["longitude"] = k["latitude"].split(",")[1]
        k["latitude"] = k["latitude"].split(",")[0]
    except Exception:
        k["longitude"] = "<MISSING>"
        k["latitude"] = "<MISSING>"
    try:
        k["address"] = k["address"].split("\r\n")
    except Exception:
        k["address"] = k["address"]

    try:
        k["city"] = k["address"][-2]
    except Exception:
        k["city"] = "<MISSING>"

    k["state"] = "<MISSING>"
    try:
        k["zip"] = k["address"][-1]
    except Exception:
        k["zip"] = "<MISSING>"

    try:
        k["address"] = " ".join(k["address"][0:-2])
    except Exception:
        k["address"] = k["address"]

    if k["city"] == "Westfield Shopping Centre":
        k["city"] = "Westfield"
        k["address"] = k["address"] + "Westfield Shopping Centre"
    if (
        k["hours"]
        == "Mon - Sun (dine in): 12-6pm (last sitting 4:45pm) Takeaway, Click & Collect and Deliveroo 12-9:30pm daily"
    ):
        k["hours"] = "Mon - Sun: 12-6pm "
    return k


def fetch_data():
    # noqa  para({"link":"https://www.wahaca.co.uk/locations/brighton/","address":"160-161 North Street\r\nBrighton\r\nBN1 1EZ"})
    logzilla = sglog.SgLogSetup().get_logger(logger_name="CRAWLER")
    url = "https://www.wahaca.co.uk/locations/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
    }
    session = SgRequests()
    son = session.get(url, headers=headers)
    soup = b4(son.text, "lxml")
    results = json.loads(
        soup.find("div", {"class": "js-locations", "data-locations": True})[
            "data-locations"
        ]
    )

    lize = utils.parallelize(
        search_space=results,
        fetch_results_for_rec=para,
        max_threads=20,
        print_stats_interval=20,
    )
    for i in lize:
        yield i

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
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


def scrape():
    url = "https://www.wahaca.co.uk/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(mapping=["link"]),
        location_name=sp.MappingField(mapping=["title"], is_required=False),
        latitude=sp.MappingField(mapping=["latitude"]),
        longitude=sp.MappingField(mapping=["longitude"]),
        street_address=sp.MappingField(
            mapping=["address"], is_required=False, value_transform=fix_comma
        ),
        city=sp.MappingField(mapping=["city"], is_required=False),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MappingField(mapping=["zip"], is_required=False),
        country_code=sp.MissingField(),
        phone=sp.MappingField(mapping=["contact", "telephone"]),
        store_number=sp.MappingField(mapping=["id"]),
        hours_of_operation=sp.MappingField(mapping=["hours"]),
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
