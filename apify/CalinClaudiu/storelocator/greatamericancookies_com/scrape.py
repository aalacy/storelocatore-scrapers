from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MissingField
from sglogging import sglog
from sgselenium import SgFirefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as b4
import json
import sgpostal.sgpostal as parser


def pass_url():
    for url in [
        "https://www.greatamericancookies.com/locations/",
        "https://www.greatamericancookies.com/locations/?international=1",
    ]:
        for item in fetch_data(url):
            yield item


def parse_details(k):
    parse = str(
        k["street_address_1"]
        + " "
        + k["street_address_2"]
        + " "
        + k["city"]
        + " "
        + k["state"]
        + " "
        + k["zip"]
    )
    addr = parser.parse_address_intl(parse)
    k["street_address"] = (
        addr.street_address_1 if addr.street_address_1 else "<MISSING>"
    )
    if addr.street_address_2:
        k["street_address"] = k["street_address"] + ", " + addr.street_address_2
    k["city"] = addr.city if addr.city else "<MISSING>"
    k["state"] = addr.state if addr.state else "<MISSING>"
    k["postcode"] = addr.postcode if addr.postcode else "<MISSING>"
    k["country"] = addr.country if addr.country else "<MISSING>"
    return k


def fetch_data(url):
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    son = ""
    with SgFirefox() as driver:
        logzilla.info(f"Getting page..")  # noqa
        driver.get(url)
        logzilla.info(f"Waiting for response to load.")  # noqa
        locs = WebDriverWait(driver, 30).until(  # noqa
            EC.visibility_of_element_located((By.XPATH, '//*[@id="locMap"]/div[2]'))
        )
        soup = b4(driver.page_source, "lxml")
        son = json.loads(soup.find("div", {"id": "mapCanvas"})["data-locations"])
        comingSoon = ["oon", "OON"]
        for i in son:
            i["type"] = "<MISSING>"
            i["hours"] = fix_hours(i["hours"])
            if any(j in i["hours"] or j in i["title"] for j in comingSoon):
                i["type"] = "Coming Soon!"
                i["hours"] = "<MISSING>"

            yield parse_details(i)

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
    except:
        h = x

    if len(h) < 2:
        h = "<MISSING>"

    return h


def fix_hours(x):
    h = []
    days = [
        "24/7",
        "Closed",
        "day",
        "Mon",
        "Tue",
        "Wed",
        "Thu",
        "Fri",
        "Sat",
        "Sun",
        "0am",
        "1am",
        "2am",
        "3am",
        "4am",
        "5am",
        "6am",
        "7am",
        "8am",
        "9am",
        "0pm",
        "1pm",
        "2pm",
        "3pm",
        "4pm",
        "5pm",
        "6pm",
        "7pm",
        "8pm",
        "9pm",
    ]
    soup = b4(x, "lxml")
    for i in soup.find_all("span", {"class": "day"}):
        if any(j in i.text for j in days):
            if len(i.text) > 2:
                h.append(i.text.strip())

    if len(h) != 0:
        h = "; ".join(h)
    else:
        h = "<MISSING>"

    if "oon!" in x:
        h = "Coming Soon!"

    backup = h
    h = []
    try:
        backup = backup.split(";")
        for i in backup:
            if len(i) > 2:
                h.append(i)
        h = "; ".join(h)
    except:
        h = backup
    return h.replace("\n", "").replace("\r", "")


def scrape():
    url = "https://www.greatamericancookies.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(
            mapping=["permalink"], is_required=False, part_of_record_identity=True
        ),
        location_name=MappingField(
            mapping=["title"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            part_of_record_identity=True,
        ),
        latitude=MappingField(mapping=["latitude"], part_of_record_identity=True),
        longitude=MappingField(mapping=["longitude"], part_of_record_identity=True),
        street_address=MappingField(
            mapping=["street_address"],
            part_of_record_identity=True,
        ),
        city=MappingField(
            mapping=["city"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            part_of_record_identity=True,
        ),
        state=MappingField(
            mapping=["state"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            part_of_record_identity=True,
        ),
        zipcode=MappingField(
            mapping=["postcode"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
            part_of_record_identity=True,
        ),
        country_code=MappingField(
            mapping=["country"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
            part_of_record_identity=True,
        ),
        phone=MappingField(
            mapping=["phone"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
            part_of_record_identity=True,
        ),
        store_number=MissingField(),
        hours_of_operation=MappingField(
            mapping=["hours"], is_required=False, part_of_record_identity=True
        ),
        location_type=MappingField(mapping=["type"], part_of_record_identity=True),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="greatamericancookies.com",
        data_fetcher=pass_url,
        field_definitions=field_defs,
        log_stats_interval=15,
        post_process_filter=lambda rec: rec.location_type() != "Coming Soon!",
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
