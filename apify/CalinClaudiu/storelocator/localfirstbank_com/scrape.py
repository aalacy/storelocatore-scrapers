from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup as b4
import json


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://localfirstbank.com/locations/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
    }

    session = SgRequests()
    son = session.get(url, headers=headers)
    soup = b4(son.text, "lxml")
    soup = soup.find(
        "script", {"type": "text/javascript", "id": "fb_custom_locations_js-js-extra"}
    )
    try:
        son = json.loads(str(soup.text).split("site_data = ", 1)[1].rsplit(";", 1)[0])
    except:
        soup = b4(son.text, "lxml")
        soup = soup.find_all("script", {"type": "text/javascript"})
        for i in soup:
            if "site_data" in i.text:
                son = json.loads(
                    str(i.text).split("site_data = ", 1)[1].rsplit(";", 1)[0]
                )

    for i in son["pointsData"]:
        yield i

    logzilla.info(f"Finished grabbing data!!")


def fix_comma(x):
    h = []

    x = x.replace("None", "")
    try:
        x = x.split(",")
        for i in x:
            if len(i) > 1:
                h.append(i)
        h = ", ".join(h)
    except:
        h = x

    if len(h) < 2:
        h = "<MISSING>"

    return h


def pretty_hours(url):

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
    }

    session = SgRequests()
    son = session.get(url, headers=headers)
    soup = b4(son.text, "lxml")
    son = json.loads(
        soup.find("script", {"type": "application/ld+json", "class": False}).text
    )
    h = []
    for i in son["openingHoursSpecification"]:
        h.append(i["dayOfWeek"][0] + ": " + i["opens"] + "-" + i["closes"])
    return "; ".join(h)


def scrape():
    url = "https://www.localfirstbank.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=["permalink"]),
        location_name=MappingField(
            mapping=["name"],
            value_transform=lambda x: x.replace("None", "<MISSING>")
            .replace("&#8217;", "'")
            .replace("&#8211;", "-"),
        ),
        latitude=MappingField(mapping=["lat"]),
        longitude=MappingField(mapping=["lng"]),
        street_address=MultiMappingField(
            mapping=[["address1"], ["address2"]],
            multi_mapping_concat_with=", ",
            value_transform=fix_comma,
        ),
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
        country_code=MissingField(),
        phone=MappingField(
            mapping=["phone_number"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        store_number=MappingField(mapping=["branch_number"]),
        hours_of_operation=MappingField(
            mapping=["permalink"], value_transform=pretty_hours, is_required=False
        ),
        location_type=MappingField(mapping=["type"], is_required=False),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="localfirstbank.com",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
