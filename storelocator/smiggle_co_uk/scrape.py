import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from webdriver_manager.chrome import ChromeDriverManager
from sgpostal.sgpostal import parse_address_intl
import ssl
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


def get_driver():
    return SgChrome(
        executable_path=ChromeDriverManager().install(),
        user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        is_headless=True,
    ).driver()


locator_domain = "https://www.smiggle.co.uk"
base_url = "https://www.smiggle.co.uk/shop/en/smiggleuk/stores/gb/gball"

country_map = {
    "GB": "United Kingdom",
    "AU": "Australia",
    "SG": "Singapore",
    "IE": "Ireland",
    "MY": "Malaysia",
    "NZ": "New Zealand",
}


def fetch_data():
    driver = get_driver()
    driver.get(base_url)
    sp1 = bs(driver.page_source, "lxml")
    store_list = json.loads(sp1.select_one("div#storeSelection").text)["storeLocator"]

    for store in store_list:
        street_address = (
            store["streetAddress"].replace("&amp;", "&").replace("&#039;", "'")
        )
        street_address = (
            "" if street_address == "." or street_address == "" else street_address
        )

        if store["shopAddress"]:
            street_address = store["shopAddress"] + " " + street_address

        zip_postal = store["zipcode"].replace(".", "")
        city = store["city"].replace("&amp;", "&").replace("&#039;", "'")

        state = store["state"]
        if state == store["country"]:
            state = ""
        zip_postal = store["zipcode"].replace(".", "")
        if store["country"] == "MY" and zip_postal:
            if not zip_postal.isdigit() or zip_postal == "0":
                zip_postal = ""

        country_code = country_map[store["country"]]

        raw_address = f"{street_address}, {city}"
        if state:
            raw_address += ", " + state
        if zip_postal:
            raw_address += ", " + zip_postal

        if country_code:
            raw_address += ", " + country_code

        addr = parse_address_intl(raw_address)
        city = addr.city
        state = addr.state
        if store["country"] != "GB":
            zip_postal = addr.postcode

        if store["country"] == "IE":
            zip_postal = city = state = ""
            _addr = raw_address.split(",")
            if "dublin" not in _addr[-2].lower():
                zip_postal = _addr[-2].strip()
            else:
                state = _addr[-2].strip()
            city = _addr[-3].strip()
            street_address = " ".join(_addr[:-3])

        latitude = store["latitude"]
        longitude = store["longitude"]
        if latitude == "-37.8" and longitude == "144.98":
            latitude = ""
            longitude = ""

        if city:
            if city == "Street":
                street_address = raw_address.split(",")[0]
                city = raw_address.split(",")[1]
            if city == "Floors":
                street_address += " Floors"

        if store["country"] == "AU" and not city:
            city = raw_address.split(",")[-4].strip()
            if (
                "Waters" in city
                or "Mount" in city
                or "Centre" in city
                or "South" in city
            ):
                city = ""

        street_address = street_address.strip()
        if street_address.startswith("."):
            street_address = street_address[1:]
        if street_address.startswith(","):
            street_address = street_address[1:]
        yield SgRecord(
            page_url=store["storeURL"],
            store_number=store["locId"],
            location_name=store["storeName"],
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            latitude=latitude,
            longitude=longitude,
            country_code=country_code,
            phone=store["phone"],
            locator_domain=locator_domain,
            hours_of_operation=store["storehours"],
            raw_address=raw_address,
        )
    if driver:
        driver.close()


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
