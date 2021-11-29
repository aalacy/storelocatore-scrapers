from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("papamurphys")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://papamurphys.ca/"
base_url = "https://papa-murphys-order-online-locations.securebrygid.com/zgrid/themes/13097/portal/index.jsp"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.restaurant")
        logger.info(f"{len(links)} found")
        for link in links:
            addr = list(link.p.stripped_strings)
            hours = []
            if len(link.select("p")) > 1:
                for hh in link.select("p")[1].stripped_strings:
                    if "delivery" in hh.lower():
                        break
                    hours.append(hh)
            yield SgRecord(
                page_url=link.select_one("a.portalbtn")["href"],
                location_name=link.h6.text.strip(),
                street_address=addr[0].replace("–", "-"),
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=" ".join(addr[1].split(",")[1].strip().split(" ")[1:]),
                country_code="CA",
                phone=addr[-1],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
