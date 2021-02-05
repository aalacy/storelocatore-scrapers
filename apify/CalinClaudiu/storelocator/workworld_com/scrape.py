from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sglogging import sglog
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

from sgrequests import SgRequests

from bs4 import BeautifulSoup as b4


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()

    ident = set()
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.AUSTRALIA],
        max_radius_miles=500,
        max_search_results=100,
    )
    for lat, lng in search:
        son = session.get(
            "https://www.workworld.com/wp-admin/admin-ajax.php?action=store_search&lat="
            + str(lat)
            + "&lng="
            + str(lng)
            + "&max_results=100&search_radius=500&autoload=1",
            headers=headers,
        ).json()
        for i in son:
            if (str(i["id"]) + str(i["permalink"])) not in ident:
                ident.add(str(i["id"]) + str(i["permalink"]))
                yield i

    logzilla.info(f"Finished grabbing data!!")  # noqa


def nice_hours(x):

    soup = b4(x, "lxml")

    h = list(soup.stripped_strings)

    if len(h) == 1:
        return "<MISSING>"
    x = ""
    if len(h) % 2 == 0:
        while len(h) > 0:
            x = x + h[0]
            x = x + ": "
            try:
                h.pop(0)
                x = x + h[0]
                x = x + "; "
            except Exception:
                continue

    return x


def scrape():
    url = "https://www.workworld.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=["permalink"]),
        location_name=MappingField(
            mapping=["store"],
            value_transform=lambda x: x.replace("&#8217;", "'").replace("&#8211;", "-"),
        ),
        latitude=MappingField(
            mapping=["lat"],
        ),
        longitude=MappingField(
            mapping=["lng"],
        ),
        street_address=MappingField(mapping=["address"]),
        city=MappingField(mapping=["city"]),
        state=MappingField(mapping=["state"]),
        zipcode=MappingField(mapping=["zip"]),
        country_code=MappingField(mapping=["country"]),
        phone=MappingField(mapping=["phone"], is_required=False),
        store_number=MappingField(mapping=["id"]),
        hours_of_operation=MappingField(mapping=["hours"], value_transform=nice_hours),
        location_type=MappingField(
            mapping=["store"],
            value_transform=lambda x: "Coming Soon"
            if any(i in x for i in ["OON", "oon"])
            else "<MISSING>",
        ),
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
