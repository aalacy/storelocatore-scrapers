from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sglogging import sglog
from sgscrape.pause_resume import CrawlStateSingleton
from sgscrape import simple_utils as utils


from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4

import json

from sgselenium import SgFirefox

logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")


def para(k):

    session = SgRequests()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    son = session.get(k["facilityOverview"]["homeUrl"], headers=headers)

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


def gen_countries(session):
    url = "https://www.hilton.com/en/locations/"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    main = session.get(url, headers=headers)
    soup = b4(main.text, "lxml")
    countries = []
    data = soup.find_all(
        "div",
        {
            "id": lambda x: x and "location-tab-panel-" in x,
            "aria-labelledby": lambda x: x and "location-tab" in x,
            "role": "tabpanel",
            "tabindex": True,
            "class": True,
        },
    )
    for alist in data:
        links = alist.find_all("a")
        for link in links:
            countries.append(
                {"text": link.text, "link": link["href"], "complete": False}
            )
    return countries


def fetch_data():
    state = CrawlStateSingleton.get_instance()
    with SgRequests(verify_ssl = False) as session:
        countries = state.get_misc_value(
            "countries", default_factory=lambda: gen_countries(session)
        )
        for country in countries:
            if not country["complete"]:
                for record in data_fetcher(country, state):
                    yield record
                country["complete"] = True
                state.set_misc_value("countries", countries)


def data_fetcher(country, state):
    url = country["link"]

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

    logzilla.info(f"Found a total of {total} hotels for country {country}")  # noqa

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
        page_url=MappingField(mapping=["facilityOverview", "homeUrl"]),
        location_name=MappingField(mapping=["name"]),
        latitude=MappingField(
            mapping=["localization", "coordinate", "latitude"],
        ),
        longitude=MappingField(
            mapping=["localization", "coordinate", "longitude"],
        ),
        street_address=MappingField(
            mapping=["address", "addressLine1"], part_of_record_identity=True
        ),
        city=MappingField(mapping=["address", "city"]),
        state=MappingField(
            mapping=["address", "state"],
            value_transform=lambda x: x.replace("None", "<MISSING>").replace(
                "Null", "<MISSING>"
            ),
        ),
        zipcode=MappingField(
            mapping=["extras", "address", "postalCode"], is_required=False
        ),
        country_code=MappingField(mapping=["address", "country"]),
        phone=MappingField(
            mapping=["contactInfo", "phoneNumber"], part_of_record_identity=True
        ),
        store_number=MappingField(mapping=["_id"], part_of_record_identity=True),
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
