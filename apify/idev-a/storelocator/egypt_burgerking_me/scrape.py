from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("burgerking")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://egypt.burgerking.me"
base_url = "https://egypt.burgerking.me/en/locations.aspx"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.address")
        for _ in locations:
            raw_address = list(_.select_one("p.info").stripped_strings)[0]
            addr = parse_address_intl(raw_address + ", Egypt")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            if city:
                if "8th Zone" in city:
                    city = ""
                elif city in raw_address.split(",")[-1]:
                    city = raw_address.split(",")[-1]
            coord = _.a["href"].split("?q=")[1].split(",")
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"].replace("Modal", ""),
                location_name=_.a.text.strip(),
                street_address=street_address.replace("Egypt", ""),
                city=city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="Egypt",
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
