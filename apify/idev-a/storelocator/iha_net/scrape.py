from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("lha")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://lha.net"
base_url = "https://lha.net/schools/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.spot a")
        for link in locations:
            page_url = locator_domain + link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            block = list(sp1.select_one("p#contact-info").stripped_strings)
            addr = block[-1].split(",")
            try:
                coord = (
                    sp1.select("p#contact-info a")[-1]["href"]
                    .split("/@")[1]
                    .split("/data")[0]
                    .split(",")
                )
            except:
                coord = ["", ""]
            yield SgRecord(
                page_url=page_url,
                location_name=" ".join(sp1.h1.stripped_strings),
                street_address=addr[0].strip(),
                city=addr[1].strip(),
                state=addr[-1].strip().split(" ")[0].strip(),
                zip_postal=addr[-1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=block[0],
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                raw_address=block[-1],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
