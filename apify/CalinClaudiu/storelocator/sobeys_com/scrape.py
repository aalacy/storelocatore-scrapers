from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MultiMappingField
from sgscrape.simple_scraper_pipeline import MissingField
from sgscrape import simple_utils as utils
from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup


def stubborn_store(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"
    }
    session = SgRequests()
    son = session.get("https://www.sobeys.com/stores/" + url, headers=headers)
    soup = BeautifulSoup(son.text, "lxml")
    k = {}
    coords = soup.find("div", {"data-lat": True, "data-lng": True})
    k["lat"] = coords["data-lat"]
    k["lng"] = coords["data-lng"]
    k["phone"] = soup.find(
        "a", {"href": lambda x: x and x.startswith("tel:")}
    ).text.strip()
    k["zip"] = soup.find("span", {"class": "postal_code"}).text.strip()
    return k


def para(idey):
    url = "https://www.sobeys.com/wp-json/wp/v2/store/" + idey
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"
    }
    session = SgRequests()
    son = session.get(url, headers=headers).json()
    try:
        son["location"]["address"]["address_1"] = son["location"]["address"][
            "address_1"
        ]
        son["location"]["address"]["address_2"] = son["location"]["address"][
            "address_2"
        ]
    except Exception:
        try:
            son["location"] = {}
            son["location"]["address"] = {}
            son["location"]["address"]["address_1"] = son["store_details"][
                "location_address_address_1"
            ]
            son["location"]["address"]["address_2"] = son["store_details"][
                "location_address_address_2"
            ]
        except Exception:
            son["location"] = {}
            son["location"]["address"] = {}
            son["location"]["address"]["address_1"] = "<MISSING>"
            son["location"]["address"]["address_2"] = "<MISSING>"

    try:
        son["location"]["coordinates"]["latitude"] = son["location"]["coordinates"][
            "latitude"
        ]
        son["location"]["coordinates"]["longitude"] = son["location"]["coordinates"][
            "longitude"
        ]
    except Exception:
        try:
            son["location"]["coordinates"] = {}
            son["location"]["coordinates"]["latitude"] = son["store_details"][
                "location_latitude"
            ]
            son["location"]["coordinates"]["longitude"] = son["store_details"][
                "location_longitude"
            ]
        except Exception:
            son["location"]["coordinates"] = {}
            son["location"]["coordinates"]["latitude"] = "<MISSING>"
            son["location"]["coordinates"]["longitude"] = "<MISSING>"
    try:
        son["location"]["address"]["city"] = son["location"]["address"]["city"]
    except Exception:
        try:
            son["location"]["address"]["city"] = son["store_details"]["city"]
        except Exception:
            son["location"]["address"]["city"] = "<MISSING>"
    if idey == "832":
        # there's no better way of doing this, they hard coded this location, so shall I...
        son["contact_details"] = {}
        son["contact_details"]["phone_details"] = {}
        son["contact_details"]["phone_details"]["phone"] = "204-832-8605"
        son["location"]["address"]["postal_code"] = "R3K 2G6"
        son["location"]["address"]["province"] = "<MISSING>"

    try:
        son["location"]["address"] = son["location"]["address"]
    except Exception:
        son["location"]["address"] = {}

    try:
        son["location"]["address"]["province"] = son["location"]["address"]["province"]
    except Exception:
        son["location"]["address"]["province"] = "<MISSING>"

    try:
        son["location"]["address"]["postal_code"] = son["location"]["address"][
            "postal_code"
        ]
    except Exception:
        son["location"]["address"]["postal_code"] = "<MISSING>"

    try:
        son["contact_details"] = son["contact_details"]
    except Exception:
        son["contact_details"] = {}

    try:
        son["contact_details"]["phone_details"] = son["contact_details"][
            "phone_details"
        ]
    except Exception:
        son["contact_details"]["phone_details"] = {}

    try:
        son["contact_details"]["phone_details"]["phone"] = son["contact_details"][
            "phone_details"
        ]["phone"]
    except Exception:
        son["contact_details"]["phone_details"]["phone"] = "<MISSING>"

    if son["location"]["address"]["province"] == "<MISSING>":
        if son["location"]["address"]["postal_code"] == "<MISSING>":
            if son["contact_details"]["phone_details"]["phone"] == "<MISSING>":
                extras = stubborn_store(son["slug"])
                son["location"]["coordinates"]["latitude"] = extras["lat"]
                son["location"]["coordinates"]["longitude"] = extras["lng"]
                son["location"]["address"]["postal_code"] = extras["zip"]
                son["contact_details"]["phone_details"]["phone"] = extras["phone"]

    return son


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://www.sobeys.com/store-locator/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"
    }
    session = SgRequests()
    son = session.get(url, headers=headers)
    soup = BeautifulSoup(son.text, "lxml")
    soup = soup.find("div", {"id": "list-stores-wrap"})
    links = []
    for i in soup.find_all("div", {"class": "store-result"}):
        links.append(i["data-id"])
    url = "https://www.sobeys.com/wp-json/wp/v2/store/"
    j = utils.parallelize(
        search_space=links,
        fetch_results_for_rec=para,
        max_threads=10,
        print_stats_interval=10,
    )
    for i in j:
        yield i
    logzilla.info(f"Finished grabbing data!!")  # noqa


def nice_hours(x):
    x = str(x)
    x = (
        x.replace("None", "<MISSING>")
        .replace("', '", "; ")
        .replace("': '", ": ")
        .replace("'", "")
        .replace("}", "")
        .replace("{", "")
    )
    if x.count("<MISSING>") == 7:
        x = "Open 24 Hours"
    return x


def scrape():
    url = "https://www.sobeys.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(
            mapping=["slug"],
            value_transform=lambda x: "https://www.sobeys.com/stores/" + x + "/",
        ),
        location_name=MappingField(mapping=["title", "rendered"]),
        latitude=MappingField(
            mapping=["location", "coordinates", "latitude"], is_required=False
        ),
        longitude=MappingField(
            mapping=["location", "coordinates", "longitude"], is_required=False
        ),
        street_address=MultiMappingField(
            mapping=[
                ["location", "address", "address_1"],
                ["location", "address", "address_2"],
            ],
            multi_mapping_concat_with=", ",
        ),
        city=MappingField(mapping=["location", "address", "city"], is_required=False),
        state=MappingField(
            mapping=["location", "address", "province"], is_required=False
        ),
        zipcode=MappingField(
            mapping=["location", "address", "postal_code"], is_required=False
        ),
        country_code=MissingField(),
        phone=MappingField(
            mapping=["contact_details", "phone_details", "phone"], is_required=False
        ),
        store_number=MappingField(mapping=["id"]),
        hours_of_operation=MappingField(
            mapping=["store_details", "hours"], value_transform=nice_hours
        ),
        location_type=MappingField(mapping=["type"]),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="sobeys.com",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=25,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
