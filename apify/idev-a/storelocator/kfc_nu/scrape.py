from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("kfc")


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://kfc.nu"
base_url = "https://kfc.nu/hitta-oss/"


def fetch_data():
    with SgRequests() as session:
        locations = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "div#map span.gmaps-marker"
        )
        for _ in locations:
            page_url = locator_domain + _["data-travel"]
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            logger.info(page_url)
            addr = list(sp1.select_one("dl.adress").stripped_strings)
            hours = []
            temp = list(sp1.select_one("dl.open").stripped_strings)
            for x in range(0, len(temp), 2):
                hours.append(f"{temp[x]} {temp[x+1]}")
            yield SgRecord(
                page_url=page_url,
                location_name=_["data-name"],
                street_address=_["data-adress"].replace("&#228;", "ä"),
                city=addr[-1],
                latitude=_["data-lat"],
                longitude=_["data-long"],
                country_code="Sweden",
                phone=_["data-phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("&#228;", "ä"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
