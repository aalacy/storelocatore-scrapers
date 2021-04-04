from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MissingField
from sgrequests import SgRequests
from sglogging import sglog
from sgzip import SearchableCountries
import sgzip
from bs4 import BeautifulSoup as b4


def determine(k):
    branch = k["fields"]["branch"]
    atm = k["fields"]["atm"]
    result = []
    if branch and atm:
        result = "Branch + ATM"
    elif branch:
        result = "Branch"
    elif atm:
        result = "ATM"
    return result


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    # 33.5114334&lng=-112.0685027
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
    }
    session = SgRequests()
    logzilla.info(  # noqa
        f"Grabbing https://www.commercebank.com/locations to get api key"  # noqa
    )  # noqa
    search = sgzip.DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=500,
        max_search_results=4000,
    )
    key = session.get("https://www.commercebank.com/locations", headers=headers)
    key = b4(key.text, "lxml")
    scripts = key.find_all("script", {"type": "text/javascript"})
    for i in scripts:
        if "CB.config.mapquestKey" in i.text:
            key = i.text
    key = key.split("CB.config.mapquestKey", 1)[1].split(";", 1)[0].strip()
    key = key.split("'", 1)[1].rsplit("'", 1)[0]
    logzilla.info(f"Found the following key: <{key}>")
    url = (
        "https://www.mapquestapi.com/search/v2/radius?key="
        + key
        + "&maxMatches=4000&units=dm&hostedData=mqap.34469_LiveTable|||&radius=500&origin="
    )  # zip
    url2 = "&ambiguities=ignore"

    search.initialize()
    coord = search.next()
    identities = set()
    while coord:
        son = session.get(url + str(coord) + url2, headers=headers).json()
        result_lats = []
        result_longs = []
        result_coords = []
        topop = 0
        if son["resultsCount"] > 0:
            for k in son["searchResults"]:
                result_lats.append(k["fields"]["latitude"])
                result_longs.append(k["fields"]["longitude"])
                if str(k["fields"]["recordId"]) not in identities:
                    identities.add(str(k["fields"]["recordId"]))
                    k["type"] = determine(k)
                    yield k
                else:
                    topop += 1
        result_coords = list(zip(result_lats, result_longs))
        logzilla.info(
            f"Coords remaining: {search.zipcodes_remaining()}; Last request yields {len(result_coords)-topop} stores."
        )
        search.update_with(result_coords)
        coord = search.next()

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


def good_hours(k):
    if (len(k)) < 2:
        return "<MISSING>"
    # DAYS_MONDAY_THROUGH_WEDNESDAY: 'Mon - Wed:',
    # DAYS_THURSDAY: 'Thursday:',
    # DAYS_FRIDAY: 'Friday:',
    # DAYS_SATURDAY: 'Saturday:',
    # DAYS_SUNDAY: 'Sunday:',
    days = ["Mon - Wed:", "Thursday:", "Friday:", "Saturday:", "Sunday:"]
    day = 0
    h = []
    k = k.split("   ")
    for i in k:
        h.append(days[day] + " " + str(i))
        day += 1
    return "; ".join(h)


def scrape():
    url = "https://www.commercebank.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MissingField(),
        location_name=MappingField(
            mapping=["name"], value_transform=lambda x: x.replace("None", "<MISSING>")
        ),
        latitude=MappingField(
            mapping=["fields", "latitude"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        longitude=MappingField(
            mapping=["fields", "longitude"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        street_address=MappingField(
            mapping=["fields", "address"], value_transform=fix_comma
        ),
        city=MappingField(
            mapping=["fields", "city"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        state=MappingField(
            mapping=["fields", "state"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        zipcode=MappingField(
            mapping=["fields", "postal_code"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        country_code=MappingField(mapping=["fields", "country"], is_required=False),
        phone=MissingField(),
        store_number=MappingField(mapping=["fields", "recordId"]),
        hours_of_operation=MappingField(
            mapping=["fields", "branch_hours"],
            raw_value_transform=good_hours,
            is_required=False,
        ),
        location_type=MappingField(mapping=["type"]),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="commercebank.com",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
