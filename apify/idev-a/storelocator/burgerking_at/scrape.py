from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("burgerking")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://burgerking.at"
base_url = "https://burgerking.at/kingfinder"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div#store-list-container table.filter-list-items tr")
        for _ in locations:
            page_url = base_url + _["data-link"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = list(sp1.select_one("div.store-adress table").tr.stripped_strings)
            hours = []
            if sp1.select("table.openingtimes"):
                hours = [
                    ": ".join(hh.stripped_strings)
                    for hh in sp1.select("table.openingtimes")[0].select("tr")
                ]
            coord = (
                sp1.select_one("div.map-distance-store a")["href"]
                .split("?daddr=")[1]
                .split(",")
            )
            yield SgRecord(
                page_url=page_url,
                store_number=page_url.split("id=")[-1],
                street_address=" ".join(addr[:-1]).replace("  ", ""),
                city=" ".join(addr[-2].split(" ")[1:]).split("/")[0].strip(),
                state=addr[-1].strip(),
                zip_postal=addr[-2].split(" ")[0].strip(),
                country_code="Austria",
                phone=sp1.select_one("div.store-adress table")
                .select("tr")[1]
                .text.strip(),
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation="; ".join(hours),
                locator_domain=locator_domain,
                raw_address=" ".join(addr).replace("  ", ""),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
