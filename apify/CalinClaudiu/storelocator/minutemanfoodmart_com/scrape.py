from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog

from sgscrape.sgrecord import SgRecord
from lxml import html
from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4
from sgscrape import sgpostal as parser
import json5


def get_locations(url):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    source = SgRequests.raise_on_err(session.get(url, headers=headers)).text
    tree = html.fromstring(source)
    soup = b4(source, "lxml")
    theScript = "".join(
        tree.xpath("//script[contains(text(), 'var locations')]/text()")
    )
    theScript = json5.loads(
        "{ data: ["
        + str(theScript.split("var locations = [ ")[1].split(",  ];")[0])
        + ",  ]}"
    )
    theScript = theScript["data"]

    stores = soup.find("div", {"class": "locations"}).find_all(
        "div", {"class": "alocation"}
    )

    for i in range(len(stores)):
        k = {}
        js_data = theScript[i]
        bs_data = list(stores[i].stripped_strings)

        if len(bs_data) == 6:
            k["lat"] = js_data["lat"] if js_data["lat"] else ""
            k["lon"] = js_data["lng"] if js_data["lng"] else ""
            k["name"] = bs_data[0]
            k["storeno"] = bs_data[0].split("#")[-1].strip()
            k["type"] = bs_data[1]
            k["phone"] = bs_data[-2]

            nice = bs_data[2].split(",")
            addressData = []
            for i in nice:
                addressData.append(i.strip())

            try:
                k["address"] = addressData[0]

                k["city"] = addressData[1]
                k["state"] = addressData[2].split(" ")[0]
                k["zip"] = addressData[2].split(" ")[1]
                k["country"] = "US"
            except Exception:
                MISSING = SgRecord.MISSING
                parsed = parser.parse_address_intl(" ".join(addressData))
                country_code = parsed.country if parsed.country else MISSING
                street_address = (
                    parsed.street_address_1 if parsed.street_address_1 else MISSING
                )
                street_address = (
                    (street_address + ", " + parsed.street_address_2)
                    if parsed.street_address_2
                    else street_address
                )
                city = parsed.city if parsed.city else MISSING
                state = parsed.state if parsed.state else MISSING
                zip_postal = parsed.postcode if parsed.postcode else MISSING
                k["address"] = street_address
                k["city"] = city
                k["state"] = state
                k["zip"] = zip_postal
                k["country"] = country_code
        else:
            k["name"] = bs_data[0]
            k["lat"] = js_data["lat"] if js_data["lat"] else ""
            k["lon"] = js_data["lng"] if js_data["lng"] else ""
            k["storeno"] = bs_data[0].split("#")[-1].strip()
            if "," not in bs_data[2]:
                bs_data.pop(2)
            nice = bs_data[2].split(",")
            addressData = []
            for i in nice:
                addressData.append(i.strip())

            k["address"] = addressData[0]

            k["city"] = addressData[1]
            k["state"] = addressData[2].split(" ")[0]
            k["zip"] = addressData[2].split(" ")[1]
            k["country"] = "US"
        yield k


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://www.minutemanfoodmart.com/locations/"
    son = get_locations(url)
    for i in son:
        yield i

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    h = []
    try:
        for i in x.split(","):
            if len(i.strip()) >= 1:
                h.append(i)
        return ", ".join(h)
    except Exception:
        return x


def scrape():
    url = "https://www.minutemanfoodmart.com/"
    page_url = "https://www.minutemanfoodmart.com/locations/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.ConstantField(page_url),
        location_name=sp.MappingField(
            mapping=["name"],
        ),
        latitude=sp.MappingField(
            mapping=["lat"],
            part_of_record_identity=True,
        ),
        longitude=sp.MappingField(
            mapping=["lon"],
            part_of_record_identity=True,
        ),
        street_address=sp.MappingField(
            mapping=["address"],
        ),
        city=sp.MappingField(
            mapping=["city"],
        ),
        state=sp.MappingField(
            mapping=["state"],
        ),
        zipcode=sp.MappingField(
            mapping=["zip"],
        ),
        country_code=sp.MappingField(mapping=["country"], is_required=False),
        phone=sp.MappingField(
            mapping=["phone"],
            is_required=False,
            part_of_record_identity=True,
        ),
        store_number=sp.MappingField(
            mapping=["storeno"],
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MissingField(),
        location_type=sp.MappingField(mapping=["type"], is_required=False),
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
