from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MultiMappingField
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup as b4
import json


def para(url):

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
    }
    session = SgRequests()
    son = session.get(
        "https://www.wellwise.ca/en-ca/stores/store/" + url, headers=headers
    )
    soup = b4(son.text, "lxml")

    try:
        data = soup.find("section", {"class": "store-details"})  # noqa
    except:
        data = "<MISSING>:<MISSING>"  # noqa

    k = {}

    k["CustomUrl"] = "https://www.wellwise.ca/en-ca/stores/store/" + url

    try:
        better_data = soup.find("google-map", {"params": True})["params"]
        better_data = better_data.split("[{", 1)[1].split("}],", 1)[0]
        better_data = json.loads("{" + str(better_data) + "}")
    except:
        better_data = "<MISSING>"

    k["data"] = better_data
    return k


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://www.wellwise.ca/en-ca/view-stores"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
    }
    session = SgRequests()
    son = session.get(url, headers=headers)

    son = son.content
    son = str(son)
    son = son.split("/stores/store/")

    stores = []
    for i in son:
        ide = i.split('"', 1)[0].strip()
        if all(j.isdigit() for j in ide):
            if ide not in stores:
                stores.append(ide)

    logzilla.info(f"Grabbing store data")  # noqa

    lize = utils.parallelize(
        search_space=stores,
        fetch_results_for_rec=para,
        max_threads=10,
        print_stats_interval=10,
    )

    for i in lize:
        yield i

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


def pretty_hours(x):

    days = ["Mo", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    h = []
    for dex, i in enumerate(x):
        h.append(days[dex] + ": " + i)
    h = "; ".join(h)

    return h


def scrape():
    url = "https://www.wellwise.ca/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=["CustomUrl"]),
        location_name=MultiMappingField(
            mapping=[["data", "storeType"], ["data", "name"]],
            multi_mapping_concat_with=" - ",
        ),
        latitude=MappingField(mapping=["data", "latitude"]),
        longitude=MappingField(mapping=["data", "longitude"]),
        street_address=MultiMappingField(
            mapping=[["data", "address"], ["data", "address2"], ["data", "address3"]],
            multi_mapping_concat_with=", ",
            value_transform=fix_comma,
        ),
        city=MappingField(
            mapping=["data", "city"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        state=MappingField(
            mapping=["data", "province"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        zipcode=MappingField(
            mapping=["data", "postalCode"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        country_code=ConstantField("CA"),
        phone=MappingField(
            mapping=["data", "phone"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        store_number=MappingField(
            mapping=["data", "storeNumber"], part_of_record_identity=True
        ),
        hours_of_operation=MappingField(
            mapping=["data", "storeHours"],
            raw_value_transform=pretty_hours,
            is_required=False,
        ),
        location_type=MappingField(mapping=["data", "storeType"]),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="wellwise.ca",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
