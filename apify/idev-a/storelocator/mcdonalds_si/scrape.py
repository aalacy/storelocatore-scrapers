from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("mcdonalds")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.mcdonalds.si"
base_url = "https://www.mcdonalds.si/restavracije/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("ul.l-restaurants-list h2 a")
        for _ in locations:
            page_url = locator_domain + _["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            block = (
                sp1.select_one("div.l-header-restaurant strong").text.strip().split(",")
            )
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in sp1.select("div.l-restaurant-info table tr")
            ]
            if hours:
                hours = hours[-7:]
            map_data = sp1.select_one("div#map")
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.select_one("div.l-header-restaurant h1").text.strip(),
                street_address=map_data["data-address"],
                city=block[1].strip().split(" ")[-1],
                zip_postal=block[1].strip().split(" ")[0],
                country_code="Slovenia",
                phone=map_data["data-tel"],
                latitude=map_data["data-map-x"],
                longitude=map_data["data-map-y"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=", ".join(block[:2]),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
