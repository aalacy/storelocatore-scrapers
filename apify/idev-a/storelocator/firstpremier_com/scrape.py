from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("firstpremier")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.firstpremier.com"
base_url = "https://www.firstpremier.com/en/pages/quick-links/locations/first-premier-bank-locations/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.block.b04block ")
        logger.info(f"{len(links)} found")
        for link in links:
            if not link.table:
                continue
            addr = list(link.td.stripped_strings)
            hours = []
            for hh in list(link.select_one("div.col-md-5").stripped_strings):
                if "Hours" in hh:
                    continue
                if "Drive" in hh:
                    break
                hours.append(hh)
            try:
                coord = link.td.a["href"].split("/@")[1].split("/data")[0].split(",")
            except:
                coord = ["", ""]
            yield SgRecord(
                page_url="https://www.firstpremier.com/en/pages/quick-links/locations/first-premier-bank-locations/",
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=addr[2],
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
