from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup as b4
import json


def para(tup):
    # https://www.pinkberry.com/stores/15083
    k = {}
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    k["index"] = tup[0]
    k["requrl"] = "https://www.americastacoshop.com/stores/" + str(tup[1])
    session = SgRequests()

    son = session.get(k["requrl"], headers=headers)
    son = son.text
    k["hours"] = son.split('"openingHours":"', 1)[1].split('"', 1)[0]

    return k


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://locator.kahalamgmt.com/locator/index.php?brand=15&mode=map&latitude=&longitude=&q=&pagesize=0"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
    }
    session = SgRequests()
    son = session.get(url, headers=headers)
    soup = b4(son.text, "lxml")
    scripts = soup.find_all("script", {"type": "text/javascript"})
    script = ""

    for i in scripts:
        if "Locator.stores[" in i.text:
            script = i.text

    script = script.split("Locator.stores[")
    script.pop(0)

    data = {}
    data["stores"] = []

    for i in script:
        data["stores"].append(
            json.loads("{" + i.split("{", 1)[1].split("}", 1)[0] + "}")
        )

    lize = utils.parallelize(
        search_space=[
            [counter, i["StoreId"]] for counter, i in enumerate(data["stores"])
        ],
        fetch_results_for_rec=para,
        max_threads=10,
        print_stats_interval=10,
    )

    for i in lize:
        data["stores"][i["index"]].update(i)
        yield data["stores"][i["index"]]

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    h = []
    try:
        x = x.split(",")
        for i in x:
            if len(i) > 1:
                h.append(i)
        h = ", ".join(h)
    except:
        h = x

    return h


def scrape():
    url = "https://www.americastacoshop.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=["requrl"]),
        location_name=MappingField(mapping=["Name"], is_required=False),
        latitude=MappingField(mapping=["Latitude"]),
        longitude=MappingField(mapping=["Longitude"]),
        street_address=MappingField(mapping=["Address"], value_transform=fix_comma),
        city=MappingField(
            mapping=["City"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        state=MappingField(
            mapping=["State"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        zipcode=MappingField(
            mapping=["Zip"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        country_code=MappingField(mapping=["CountryCode"]),
        phone=MappingField(
            mapping=["Phone"],
            value_transform=lambda x: x.replace("() -", "<MISSING>"),
            is_required=False,
        ),
        store_number=MappingField(mapping=["StoreId"]),
        hours_of_operation=MappingField(mapping=["hours"], is_required=False),
        location_type=MappingField(mapping=["StatusName"], is_required=False),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="pinkberry.com",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
