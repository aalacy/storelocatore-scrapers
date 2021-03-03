from sgscrape import simple_scraper_pipeline as sp
from sgscrape import sgpostal as parser
from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://www.covenanthealthcare.com/ch/locations?search=executesearch"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    soup = b4(session.get(url, headers=headers).text, "lxml")

    allscripts = soup.find_all("script", {"type": "text/javascript"})
    thescript = ""
    for i in allscripts:
        if "https://www.google.com/mapfiles/markerA.png" in i.text:
            thescript = i.text

    data = thescript.split("marker;")
    data.pop(0)
    data.pop(-1)
    for i in data:
        k = {}

        try:
            coords = i.split("maps.LatLng(", 1)[1].split(")", 1)[0].split(",")
        except Exception:
            coords = ["<MISSING>", "<MISSING>"]

        k["lat"] = coords[0]
        k["lng"] = coords[1]

        try:
            k["name"] = i.split("title:", 1)[1].split("',", 1)[0]
            k["name"] = k["name"].replace("'", "", 1)
        except Exception:
            k["name"] = "<MISSING>"

        soup = b4(
            str(
                i.split("html", 1)[1]
                .split("'", 1)[1]
                .split("});", 1)[0]
                .rsplit("'", 1)[0]
            ),
            "lxml",
        )
        raw_addr = list(soup.stripped_strings)
        raw_addr.pop(0)
        raw_addr = " ".join(raw_addr)
        parsed = parser.parse_address_usa(raw_addr)
        k["raw_addr"] = raw_addr
        k["country"] = parsed.country if parsed.country else "<MISSING>"
        k["state"] = parsed.state if parsed.state else "<MISSING>"
        k["postcode"] = parsed.postcode if parsed.postcode else "<MISSING>"
        k["city"] = parsed.city if parsed.city else "<MISSING>"
        k["street_address"] = (
            parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
        )
        k["street_address"] = (
            k["street_address"] + parsed.street_address_2
            if parsed.street_address_2
            else k["street_address"]
        )
        yield k

    logzilla.info(f"Finished grabbing data!!")  # noqa


def scrape():
    url = "https://www.covenanthealthcare.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MissingField(),
        location_name=sp.MappingField(
            mapping=["name"],
        ),
        latitude=sp.MappingField(
            mapping=["lat"],
        ),
        longitude=sp.MappingField(
            mapping=["lng"],
        ),
        street_address=sp.MappingField(
            mapping=["street_address"],
        ),
        city=sp.MappingField(
            mapping=["city"],
        ),
        state=sp.MappingField(
            mapping=["state"],
        ),
        zipcode=sp.MappingField(
            mapping=["postcode"],
        ),
        country_code=sp.MappingField(
            mapping=["country"],
        ),
        phone=sp.MissingField(),
        store_number=sp.MissingField(),
        hours_of_operation=sp.MissingField(),
        location_type=sp.MissingField(),
        raw_address=sp.MappingField(
            mapping=["raw_addr"],
        ),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
