from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sglogging import sglog as loggie
from bs4 import BeautifulSoup as b4
from actually_scrape import fetch_germany_ISH  # noqa

logerilla = loggie.SgLogSetup().get_logger(logger_name="Scraper")


def getTestCountries(session):
    url = "https://corporate.mcdonalds.com/corpmcd/our-company/where-we-operate.html"
    headers = {}
    headers[
        "user-agent"
    ] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    soup = b4(session.get(url, headers=headers).text, "lxml")
    soup = soup.find_all("div", {"class": ["columncontrol", "parbase"]})
    countries = []
    for div in soup:
        for link in div.find_all("a", {"href": True}):
            if link["href"] != "#top":
                if all(j not in link["href"] for j in [":", "/", "www", "http"]):
                    continue
                countries.append(
                    {
                        "text": link.text
                        if len(link.text) > 0
                        else "Unknown{}".format(link["href"]),
                        "page": link["href"],
                    }
                )

    return countries


def fetch_data():
    countries = None
    with SgRequests() as session:
        countries = getTestCountries(session)
    for country in countries:
        try:
            countryData = fetch_germany_ISH(country)
            for i in countryData:
                yield i
        except Exception as e:
            logerilla.error(f"OOPSIE:\n\n{e}")  # noqa
            pass  # lul


def fix_comma(x):
    h = []
    try:
        for i in x.split(","):
            if len(i.strip()) >= 1:
                h.append(i)
        return ", ".join(h).replace("  ", " ")
    except Exception:
        return x.replace("  ", " ")


def better_hours(x):
    if "hours" in x:
        return x.replace("'", "").replace("{", "").replace("}", "").replace("hours", "")
    return x


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(
            mapping=["locator_domain"],
        ),
        page_url=sp.MappingField(
            mapping=["page_url"],
            is_required=False,
        ),
        location_name=sp.MappingField(
            mapping=["location_name"],
            is_required=False,
            part_of_record_identity=True,
        ),
        latitude=sp.MappingField(
            mapping=["latitude"],
            is_required=False,
            part_of_record_identity=True,
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
            is_required=False,
            part_of_record_identity=True,
        ),
        street_address=sp.MappingField(
            mapping=["street_address"],
            is_required=False,
            part_of_record_identity=True,
        ),
        city=sp.MappingField(mapping=["city"], is_required=False),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MappingField(mapping=["zipcode"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"], is_required=False),
        phone=sp.MappingField(
            mapping=["phone"],
            is_required=False,
        ),
        store_number=sp.MappingField(
            mapping=["store_number"],
            is_required=False,
        ),
        hours_of_operation=sp.MappingField(
            mapping=["hours_of_operation"],
            is_required=False,
            value_transform=better_hours,
        ),
        location_type=sp.MappingField(mapping=["location_type"], is_required=False),
        raw_address=sp.MappingField(mapping=["raw_address"], is_required=False),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=1000,
        duplicate_streak_failure_factor=100,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
