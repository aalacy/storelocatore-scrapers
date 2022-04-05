from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MissingField
from sgscrape.simple_scraper_pipeline import MultiMappingField
from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import sglog
from bs4 import BeautifulSoup as b4
import json


def gimme_hours(soup):
    soup = b4(soup, "lxml")
    potH = soup.find_all("ul")
    hours = []
    data = None
    for h in potH:
        if "ours" in h:
            data = h.find_all("li")
    if data:
        for i in data:
            hours.append(
                str(
                    i.find("span", {"class": "day"}).text
                    + ": "
                    + i.find("span", {"class": "hours"}).text
                )
            )
    return "; ".join(hours)


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")

    def search_api(session, long):
        url = "https://www.loansbyworld.com/api/yext/geosearch"
        headers = {}

        headers["Content-Type"] = "application/json"
        data = str('{"location":"' + f"{long}" + '","radius":1000}')

        resp = session.post(url, headers=headers, data=data).json()
        return resp["data"]

    def fetch_sub(session, k):
        headers = {}
        headers[
            "user-agent"
        ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36"

        #%5Bstate%5D/%5Bcity%5D/%5BpostalCode%5D/%5BstoreId% # noqa
        # https://www.loansbyworld.com/locations/alabama/alabaster/35007/1521 # noqa
        url = str(
            f"https://www.loansbyworld.com/locations/k['state']['id']/k['address']['city']/k['address']['postalCode']/k['id']"
        )
        resp = session.get(url, headers=headers, data=data)
        k["hours"] = gimme_hours(resp.text)

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=25,
        max_search_results=None,
    )

    with SgRequests() as session:
        for long in search:
            for result in search_api(session, long):
                try:
                    k = fetch_sub(session, result)
                    try:
                        k["address"]["line2"] = k["address"]["line2"]
                    except Exception:
                        k["address"]["line2"] = ""
                except Exception:
                    k = result
                    k["hours"] = ""
                    yield k


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


def scrape():
    url = "https://www.loansbyworld.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MissingField(),
        location_name=MappingField(
            mapping=["store"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            part_of_record_identity=True,
        ),
        latitude=MappingField(
            mapping=["latitude"],
            part_of_record_identity=True,
        ),
        longitude=MappingField(mapping=["longitude"]),
        street_address=MultiMappingField(
            mapping=[["address", "line1"], ["address", "line2"]],
            multi_mapping_concat_with=", ",
            value_transform=fix_comma,
            is_required=False,
        ),
        city=MappingField(
            mapping=["address", "city"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        state=MappingField(
            mapping=["address", "region"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        zipcode=MappingField(
            mapping=["address", "postalCode"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        country_code=MappingField(mapping=["address", "countryCode"]),
        phone=MappingField(
            mapping=["phone"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        store_number=MappingField(
            mapping=["id"],
            part_of_record_identity=True,
        ),
        hours_of_operation=MappingField(mapping=["hours"], is_required=False),
        location_type=MissingField(),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="ajsfinefoods.com",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
