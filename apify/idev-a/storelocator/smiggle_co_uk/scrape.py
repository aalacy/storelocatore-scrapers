import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from webdriver_manager.chrome import ChromeDriverManager
import ssl

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
_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    driver = get_driver()
    driver.get(base_url)
    sp1 = bs(driver.page_source, "lxml")
    store_list = json.loads(sp1.select_one("div#storeSelection").text)["storeLocator"]

    for store in store_list:
        shop_address = store["shopAddress"].replace("&amp;", "&").replace("&#039;", "'")
        shop_address = "" if shop_address == "." or shop_address == "" else shop_address
        street_address = (
            store["streetAddress"].replace("&amp;", "&").replace("&#039;", "'")
        )
        street_address = (
            "" if street_address == "." or street_address == "" else street_address
        )
        if shop_address != "":
            street_address = (
                shop_address
                if street_address == ""
                else shop_address + ", " + street_address
            )

        zip_postal = store["zipcode"].replace(".", "")
        city = store["city"].replace("&amp;", "&").replace("&#039;", "'")
        if city in [
            "Centre, 17 Victoria St",
            "Cwmbran Shopping Centre",
            "300 Cornwall Street",
            "12 Swan Walk",
            "26 Bridge Street",
            "2 Union Street",
            "Bullring Shopping Centre",
            "St Nicholas Way",
            "Trafford Boulevard",
            "1 Utama Shopping Centre",
            "Lot No G-01/1-01/2-01",
            "Ground,1St,2Nd,3Rd Floors",
            "Lot No G-01/1-01/2-01",
            "#03-01 Bugis Junction",
        ]:
            street_address += " " + city
            city = ""
        else:
            cc = city.split()
            if cc and cc[-1].isdigit():
                if not zip_postal:
                    zip_postal = cc[-1]
                city = " ".join(cc[:-1])
        city = (
            city.split(",")[0]
            .replace("G51 4Bn", "")
            .replace("Sw3 4Nd", "")
            .replace("90", "")
            .replace("City Centre", "")
            .replace("Bugis Junction", "")
            .replace("#01 89/90 Nex", "")
            .replace("United Square", "")
            .strip()
        )
        if city.isdigit():
            zip_postal = city
            city = ""

        if city == "40170 Shah Alam Selangor":
            zip_postal = "40170"
            city = "Shah Alam"
            state = "Selangor"

        if city == "#01 89/ Nex":
            street_address += " " + city
            city = ""

        if street_address.endswith(","):
            street_address = street_address[:-1]

        state = store["state"]
        if state == store["country"]:
            state = ""
        yield SgRecord(
            page_url=store["storeURL"],
            store_number=store["locId"],
            location_name=store["storeName"],
            street_address=street_address,
            city=city.split(",")[0]
            .replace("G51 4Bn", "")
            .replace("Sw3 4Nd", "")
            .replace("90", "")
            .replace("City Centre", "")
            .replace("Robina Town Centre", "")
            .strip(),
            state=state,
            zip_postal=store["zipcode"].replace(".", ""),
            latitude=store["latitude"],
            longitude=store["longitude"],
            country_code=store["country"],
            phone=store["phone"],
            locator_domain=locator_domain,
            hours_of_operation=store["storehours"],
        )
    if driver:
        driver.close()


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
