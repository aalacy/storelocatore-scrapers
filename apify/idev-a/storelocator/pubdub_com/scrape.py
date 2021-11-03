from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs
import re
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("pubdub")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://pubdub.com/"
base_url = "https://pubdub.com/locations/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.location-list div.card")
        for _ in locations:
            addr = parse_address_intl(_.address.p.text.strip())
            sp = bs(session.get(_.h2.a["href"], headers=_headers).text, "lxml")
            hours = [hh.text for hh in sp.select("p.hours")]
            if not hours:
                hours = [
                    " ".join(hh.stripped_strings)
                    for hh in sp.select("div.hour-block")[0].select("ul li")
                ]
            logger.info(_.h2.a["href"])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2
            yield SgRecord(
                page_url=_.h2.a["href"],
                location_name=_.h2.text,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=_.find("a", href=re.compile(r"tel:")).text.strip(),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("|", ":"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
