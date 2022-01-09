from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("makro")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.makro.co.uk"
base_url = "https://www.makro.co.uk/stores.html"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div#cb_id_CONTENT table td a")
        for link in locations:
            page_url = locator_domain + link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = list(sp1.select("div#cb_id_CONTENT ul")[0].stripped_strings)
            raw_address = ", ".join(
                list(sp1.select("div#cb_id_CONTENT ul")[-1].stripped_strings)
            )
            addr = parse_address_intl(raw_address + ", United Kingdom")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.select_one("div#cb_id_CONTENT h1").text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=raw_address.split(",")[-1],
                country_code="UK",
                phone=list(sp1.select("div#cb_id_CONTENT ul")[1].stripped_strings)[0]
                .split(":")[-1]
                .strip(),
                latitude="",
                longitude="",
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
