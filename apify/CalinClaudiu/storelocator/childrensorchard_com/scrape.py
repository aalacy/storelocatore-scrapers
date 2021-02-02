from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MultiMappingField
from sgscrape.simple_scraper_pipeline import MissingField
from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4
import json


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://www.childrensorchard.com/store-locator/"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    soup = b4(session.get(url, headers=headers).text, "lxml")

    for i in soup.find_all("script"):
        if "var storeData =" in i.text:
            k = i.text

    k = '{"stores":' + k.split("var storeData = ", 1)[1].split("}];", 1)[0] + "}]}"
    son = json.loads(k)
    for i in son["stores"]:
        yield i
    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    try:
        x = x.split(",")
        h = []
        for i in x:
            if len(i) > 2:
                h.append(i)
        return ", ".join(h)
    except Exception:
        return x


def html_hours(x):
    soup = b4(x, "lxml")
    markers = [
        "PM",
        "AM",
        "A.M",
        "P.M",
        "Mon",
        "Sat",
        "Sun",
        "Tue",
        "Wed",
        "Thu",
        "Fri",
        "y:",
    ]
    unwanted = [
        "APPOINTMENTS",
        "ustomers",
        "items",
        "call",
        "availability",
        "Note:",
        "year",
        "Appointments",
        "HALLOWEEN",
        "enforcing",
    ]

    hours = []
    h = soup.stripped_strings
    for i in h:
        if any(j in i for j in markers) and not any(p in i for p in unwanted):
            hours.append(i)

    return "; ".join(hours)


def determine_type(x):
    if "Location Closed" in x:
        return "Permanently Closed"
    else:
        return "<MISSING>"


def scrape():
    url = "https://www.childrensorchard.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=["storeurl"]),
        location_name=MappingField(mapping=["name"]),
        latitude=MappingField(
            mapping=["lat"],
        ),
        longitude=MappingField(
            mapping=["lng"],
        ),
        street_address=MultiMappingField(
            mapping=[["street"], ["streettwo"]],
            multi_mapping_concat_with=",",
            value_transform=fix_comma,
        ),
        city=MappingField(mapping=["city"]),
        state=MappingField(
            mapping=["state"], value_transform=lambda x: x.replace("Wisconsin", "WI")
        ),
        zipcode=MappingField(mapping=["zip"]),
        country_code=MissingField(),
        phone=MappingField(
            mapping=["tel"],
            value_transform=lambda x: "<MISSING>" if "losed" in x else x,
        ),
        store_number=MissingField(),
        hours_of_operation=MappingField(mapping=["hours"], value_transform=html_hours),
        location_type=MappingField(mapping=["tel"], value_transform=determine_type),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
