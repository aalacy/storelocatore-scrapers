from sgscrape import simple_scraper_pipeline as sp
from sglogging import SgLogSetup
from sgselenium import SgChrome
from bs4 import BeautifulSoup as b4
import json
import ssl

logger = SgLogSetup().get_logger("raisingcanes_com")
try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    def from_sitemap(session):
        url = "http://www.raisingcanes.com/sitemap.xml"
        session.get(url)
        soup = b4(session.page_source, "lxml")
        links = soup.find_all("url")
        for link in links:
            if "https://www.raisingcanes.com/location/" in link.loc.text:
                yield link.loc.text.rsplit("/", 1)[-1]

    with SgChrome() as session:
        for index in from_sitemap(session):
            url = str(
                f"http://www.raisingcanes.com/page-data/location/{index}/page-data.json"
            )
            session.get(url)
            data = json.loads(session.page_source)
            yield data["result"]["data"]


def scrape():
    url = "https://www.raisingcanes.com"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["workdayLocations", "PresentationID"],
            value_transform=lambda x: str(
                "https://www.raisingcanes.com/location/" + str(x)
            ),
            part_of_record_identity=True,
        ),
        location_name=sp.MappingField(
            mapping=["workdayLocations", "Nickname"],
            part_of_record_identity=True,
        ),
        latitude=sp.MappingField(
            mapping=["prismicStoreLocation", "data", "coordinates", "latitude"],
            part_of_record_identity=True,
            is_required=False,
        ),
        longitude=sp.MappingField(
            mapping=["prismicStoreLocation", "data", "coordinates", "longitude"],
            is_required=False,
        ),
        street_address=sp.MappingField(
            mapping=["workdayLocations", "Primary_Address_Line_1"],
            part_of_record_identity=True,
        ),
        city=sp.MappingField(
            mapping=["workdayLocations", "city"],
        ),
        state=sp.MappingField(
            mapping=["workdayLocations", "INT_Location_State"],
        ),
        zipcode=sp.MappingField(
            mapping=["workdayLocations", "Primary_Address_Postal_Code"],
        ),
        country_code=sp.MissingField(),
        phone=sp.MappingField(
            mapping=["workdayLocations", "Phone_Number_Primary"],
        ),
        store_number=sp.MappingField(
            mapping=["workdayLocations", "PresentationID"],
        ),
        hours_of_operation=sp.MappingField(
            mapping=["workdayLocations", "Hours"],
            is_required=False,
            part_of_record_identity=True,
        ),
        location_type=sp.MappingField(
            mapping=["workdayLocations", "birthdate"],
        ),
        raw_address=sp.MissingField(),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
        duplicate_streak_failure_factor=-1,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
