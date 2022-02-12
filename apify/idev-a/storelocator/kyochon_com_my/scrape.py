from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.kyochon.com.my"
base_url = "https://www.kyochon.com.my/locations/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.outlet-item")
        for _ in locations:
            raw_address = (
                _.select_one("div.outlet-address")
                .text.replace("\n", " ")
                .replace("S22 & S23, Aeon Mall Nilai,", "")
                .replace("4-G", "4G")
                .replace("\r", "")
                .strip()
            )
            addr = parse_address_intl(raw_address + ", Malaysia")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            coord = _.select_one("a.outlet-title")["rel"][0].split(",")
            phone = ""
            if _.select_one("div.outlet-phone"):
                phone = _.select_one("div.outlet-phone").text.strip()
            city = addr.city
            if city:
                city = city.replace(".", "")
            state = addr.state
            if state:
                state = state.replace(".", "")
            zip_postal = addr.postcode
            if not zip_postal:
                if "50480" in raw_address:
                    zip_postal = "50480"
                    street_address = raw_address.split("50480")[0].strip()
                elif "47620" in raw_address:
                    zip_postal = "47620"
                    street_address = raw_address.split("47620")[0].strip()
            yield SgRecord(
                page_url=base_url,
                store_number=_["rel"],
                location_name=_.select_one("a.outlet-title").text.strip(),
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code="MY",
                phone=phone.replace("\u200e", ""),
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation=_.select_one("div.outlet-operating")
                .text.split("Last")[0]
                .strip(),
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
