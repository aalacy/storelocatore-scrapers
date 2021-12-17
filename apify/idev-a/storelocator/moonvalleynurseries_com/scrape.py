from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("moonvalleynurseries")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.moonvalleynurseries.com/"
base_url = "https://www.moonvalleynurseries.com/locations"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div#maintabContent div.subcontent-bg")
        for _ in locations:
            page_url = locator_domain + _.a["href"]
            raw_address = " ".join(_.p.stripped_strings)
            if not raw_address or "Contact" in raw_address:
                continue
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            if "Contact" in raw_address:
                street_address = city = ""
            else:
                street_address = street_address
                city = addr.city
            yield SgRecord(
                page_url=page_url,
                location_name=_.h6.text.strip(),
                street_address=street_address,
                city=city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=_.select_one("p a").text.strip(),
                locator_domain=locator_domain,
                raw_address=raw_address.replace("\n", " "),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
