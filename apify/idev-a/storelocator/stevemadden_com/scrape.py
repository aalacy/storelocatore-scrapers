from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("stevemadden")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.stevemadden.com"
base_url = "https://stores.boldapps.net/front-end/get_surrounding_stores.php?shop=stevemadden.myshopify.com&latitude=40.7135097&longitude=-73.9859414&max_distance=50000&limit=1000&calc_distance=1"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["stores"]
        for loc in locations:
            data = bs(loc["summary"], "lxml")
            hours = []
            if data.select_one(".hours"):
                temp = data.select_one(".hours").stripped_strings
                for hh in temp:
                    if "christmas" in hh.lower() or "holiday" in hh.lower():
                        break
                    hours.append(hh.replace('"', ""))
            phone = ""
            if data.select_one(".phone"):
                phone = data.select_one(".phone").text.strip()
            state = ""
            if data.select_one(".prov_state"):
                state = data.select_one(".prov_state").text.strip()
            city = ""
            if data.select_one(".city"):
                city = data.select_one(".city").text.strip()
            zip_postal = ""
            if data.select_one(".postal_zip"):
                zip_postal = data.select_one(".postal_zip").text.strip()
            street_address = data.select_one(".address").text.strip() or ""
            if (
                data.select_one(".address2")
                and data.select_one(".address2").text.strip() != "NULL"
            ):
                street_address += " " + data.select_one(".address2").text.strip()
            if street_address.endswith(","):
                street_address = street_address[:-1]
            if city in street_address or (state and state in street_address):
                addr = parse_address_intl(street_address)
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
            if street_address:
                street_address = street_address.replace("# ", "#")
            if "NULL" in hours:
                hours = []
            country_code = ""
            if data.select_one(".country"):
                country_code = data.select_one(".country").text.strip()
            if not country_code:
                country_code = loc["country"]
            yield SgRecord(
                page_url="https://www.stevemadden.com/apps/store-locator",
                store_number=loc["store_id"],
                location_name=loc["name"],
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                latitude=loc["lat"],
                longitude=loc["lng"],
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STATE,
                    SgRecord.Headers.ZIP,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
