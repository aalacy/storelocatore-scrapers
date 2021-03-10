from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MultiMappingField
from sgscrape.simple_scraper_pipeline import MissingField
from sglogging import sglog

from sgscrape import simple_utils as utils


from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4

import json


def para(k):

    session = SgRequests()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    son = session.get("https://www.premiertruck.com/" + k["web"], headers=headers)

    soup = b4(son.text, "lxml")
    days = list(
        soup.find("div", {"class": "table-responsive"}).find("thead").stripped_strings
    )
    hours = (
        soup.find("div", {"class": "table-responsive"})
        .find("tbody")
        .find("tr")
        .find_all("td")
    )
    h = []
    for i in hours:
        h.append(" ".join(list(i.stripped_strings)))
    hours = h

    if len(days) > 7:
        days.pop(0)
    k["hours"] = []
    prefix = hours[0]
    hours.pop(0)
    for i in days:
        k["hours"].append(i + ": " + hours[0])
        hours.pop(0)
    k["hours"] = prefix + ": " + "; ".join(k["hours"])

    if len(k["phone"]) < 8:
        candidates = soup.find_all("a", {"href": lambda x: x and "tel:" in x})
        phones = []
        phones.append("<MISSING>")
        for i in candidates:
            phones.append(i["href"].split("tel:")[1].strip())
        k["phone"] = phones[-1]

    return k


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://images.motorcar.com/fonts/dealerlocator/data/locations.json"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    son = session.get(url, headers=headers).text
    son = '{"stores":' + son + "}"
    son = json.loads(son)
    lize = utils.parallelize(
        search_space=son["stores"],
        fetch_results_for_rec=para,
        max_threads=10,
        print_stats_interval=10,
    )

    for i in lize:
        yield i

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_hours(x):
    try:
        h = []
        x = x.split(",")
        for i in x:
            if len(i) > 3:
                h.append(i)
        return ",".join(h)
    except Exception:
        return x


def scrape():
    url = "https://www.premiertruck.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(
            mapping=["web"],
            value_transform=lambda x: str(url + x)
            .replace("//", "/")
            .replace("https:/", "https://"),
        ),
        location_name=MappingField(mapping=["name"]),
        latitude=MappingField(
            mapping=["lat"],
        ),
        longitude=MappingField(
            mapping=["lng"],
        ),
        street_address=MultiMappingField(
            mapping=[["address"], ["address2"]],
            multi_mapping_concat_with=",",
            value_transform=fix_hours,
        ),
        city=MappingField(mapping=["city"]),
        state=MappingField(mapping=["state"]),
        zipcode=MappingField(
            mapping=["postal"],
            value_transform=lambda x: x.replace("Canada", "").strip(),
        ),
        country_code=MappingField(
            mapping=["postal"],
            value_transform=lambda x: "CA" if " " in x.strip() else "US",
        ),
        phone=MappingField(mapping=["phone"], is_required=False),
        store_number=MappingField(mapping=["id"]),
        hours_of_operation=MappingField(mapping=["hours"]),
        location_type=MissingField(),
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
