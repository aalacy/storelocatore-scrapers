from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sgpostal import sgpostal as parser

session = SgRequests()
logzilla = sglog.SgLogSetup().get_logger(logger_name="checkmate")
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"
}


def get_store(url, country):

    logzilla.info(url)
    r = session.get(url, headers=headers)
    k = {}
    soup = BeautifulSoup(r.text, "lxml")
    data = soup.find("main", {"id": "store-container", "class": True, "data-id": True})
    k["url"] = url
    try:
        k["name"] = data.find("h1", {"class": "store__title"}).text
    except:
        k["name"] = "<MISSING>"

    if k["name"] == "":
        try:
            k["name"] = data.find("h2", {"class": "store__subtitle"}).text
        except:
            k["name"] = "<MISSING>"

    try:
        k["lat"] = data["data-store-lat"]
    except:
        k["lat"] = "<MISSING>"

    try:
        k["lng"] = data["data-store-lng"]
    except:
        k["lng"] = "<MISSING>"

    k["address"] = "<MISSING>"
    k["city"] = "<MISSING>"
    k["state"] = "<MISSING>"
    k["zip"] = "<MISSING>"

    try:
        raw_address = (
            data.find("li", {"class": "store__loc-address"})
            .find("span", {"class": "text"})
            .text
        )
        formatted_addr = parser.parse_address_intl(raw_address)
        k["address"] = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            k["address"] = k["address"] + ", " + formatted_addr.street_address_2

        if k["address"] is None:
            k["address"] = "<MISSING>"

        k["city"] = formatted_addr.city
        if k["city"] is None:
            k["city"] = "<MISSING>"

        k["state"] = formatted_addr.state
        if k["state"] is None:
            k["state"] = "<MISSING>"

        k["zip"] = formatted_addr.postcode
        if k["zip"] is None:
            k["zip"] = "<MISSING>"
    except:
        pass

    k["country"] = country

    try:
        k["phone"] = (
            data.find("a", {"class": "phone"}).find("span", {"class": "text"}).text
        )
    except:
        k["phone"] = "<MISSING>"

    try:
        k["id"] = data["data-id"]
    except:
        k["id"] = "<MISSING>"

    try:
        j = []
        k["hours"] = data.find("div", {"class": "store__hours"}).find(
            "ul", {"data-expandable-area": True, "data-expandable": True}
        )
        k["hours"] = k["hours"].find_all("li")
        for i in k["hours"]:
            j.append(i.text)
        k["hours"] = "; ".join(j)
        k["hours"] = k["hours"].replace("\n", " ")

    except:
        k["hours"] = "<MISSING>"

    try:
        k["type"] = " ".join(data["class"])
        k["type"] = k["type"].split("type-")[1].split(" ", 1)[0]
    except:
        k["type"] = "<MISSING>"
    return k


def fetch_data():
    url = "https://www.armaniexchange.com/experience/us/store-locator"

    logzilla.info(f"Generating request links")  # noqa
    son = session.get(url, headers=headers)
    soup = BeautifulSoup(son.text, "lxml")
    gen = soup.find_all("li", {"class": "store-locator__stores-list-item"})
    for i in gen:
        country = (
            i.find("button", {"class": "store-locator__stores-button"})
            .find("span", {"class": "text"})
            .text
        )
        links = [
            j["href"]
            for j in i.find("div", {"class": "store-locator__stores-details"}).find_all(
                "a", {"class": "store-locator__stores-details-name"}
            )
        ]

        logzilla.info(f"Grabbing {len(links)} locations from {country}")
        for link in links:
            k = get_store(link, country)
            yield k

    logzilla.info(f"Finished grabbing data!!")  # noqa


def scrape():
    url = "https://armaniexchange.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=["url"]),
        location_name=MappingField(mapping=["name"]),
        latitude=MappingField(mapping=["lat"]),
        longitude=MappingField(mapping=["lng"]),
        street_address=MappingField(mapping=["address"]),
        city=MappingField(mapping=["city"]),
        state=MappingField(mapping=["state"]),
        zipcode=MappingField(mapping=["zip"]),
        country_code=MappingField(mapping=["country"]),
        phone=MappingField(mapping=["phone"]),
        store_number=MappingField(mapping=["id"], part_of_record_identity=True),
        hours_of_operation=MappingField(mapping=["hours"]),
        location_type=MappingField(mapping=["type"]),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="armaniexchange.com",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=25,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
