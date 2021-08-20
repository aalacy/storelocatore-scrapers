from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sglogging import sglog

from sgscrape import simple_utils as utils


from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4

import json

from sgselenium import SgFirefox


def para(k):

    session = SgRequests()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    son = session.get(k["homeUrl"], headers=headers)

    soup = b4(son.text, "lxml")

    allscripts = soup.find_all("script", {"type": "application/ld+json"})

    data = {}
    k["extras"] = {}
    k["extras"]["address"] = {}
    k["extras"]["address"]["postalCode"] = "<MISSING>"
    for i in allscripts:
        if "postalCode" in i.text:
            z = i.text.replace("\n", "")
            data = json.loads(z)

    k["extras"] = data

    return k


def fetch_data():
    # noqa print(para({"homeUrl":"https://www.hilton.com/en/hotels/bhxbnhx-hampton-birmingham-jewellery-quarter/"}))
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://www.hilton.com/en/locations/united-kingdom/"

    masterdata = []

    with SgFirefox() as driver:
        driver.get(url)
        for r in driver.requests:
            if "/graphql/customer" in r.path:
                data = r.response.body
                data = json.loads(data)
                masterdata.append(data)

    total = 0
    allhotels = []
    for i in masterdata:
        try:
            total = total + len(i["data"]["hotelSummaryOptions"]["hotels"])
            for j in i["data"]["hotelSummaryOptions"]["hotels"]:
                allhotels.append(j)

        except Exception:
            continue

    logzilla.info(f"Found a total of {total} hotels")  # noqa

    lize = utils.parallelize(
        search_space=allhotels,
        fetch_results_for_rec=para,
        max_threads=10,
        print_stats_interval=10,
    )

    for j in lize:
        yield j

    logzilla.info(f"Finished grabbing data!!")  # noqa


def scrape():
    url = "https://www.hilton.com/en/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=["homeUrl"]),
        location_name=MappingField(mapping=["name"]),
        latitude=MappingField(
            mapping=["coordinate", "latitude"],
        ),
        longitude=MappingField(
            mapping=["coordinate", "longitude"],
        ),
        street_address=MappingField(
            mapping=["address", "addressLine1"],
        ),
        city=MappingField(mapping=["address", "city"]),
        state=MappingField(mapping=["address", "state"]),
        zipcode=MappingField(
            mapping=["extras", "address", "postalCode"], is_required=False
        ),
        country_code=MappingField(mapping=["address", "country"]),
        phone=MappingField(mapping=["phoneNumber"]),
        store_number=MappingField(mapping=["_id"]),
        hours_of_operation=MappingField(
            mapping=["open"],
            value_transform=lambda x: "Possibly Closed"
            if x == "FALSE"
            else "<MISSING>",
        ),
        location_type=MappingField(mapping=["brandCode"]),
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
