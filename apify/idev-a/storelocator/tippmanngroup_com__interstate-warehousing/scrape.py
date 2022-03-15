from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("tippmanngroup")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.tippmanngroup.com"
base_url = "https://tippmanngroup.com/interstate-warehousing/locations"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.location")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + link.select("a")[-1]["href"]
            logger.info(page_url)
            res = session.get(page_url, headers=_headers).text
            sp1 = bs(res, "lxml")
            addr = list(link.select_one("div.toggle").stripped_strings)
            coord = (
                sp1.iframe["src"]
                .split("!2d")[1]
                .split("!3m")[0]
                .split("!2m")[0]
                .split("!3d")
            )
            temp = " ".join(addr[:2])
            raw_address = " ".join([tt.strip() for tt in temp.split() if tt.strip()])
            yield SgRecord(
                page_url=page_url,
                store_number=link.a["data-location"],
                location_name=link.a.text.strip().replace("–", "-"),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split()[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split()[-1].strip(),
                country_code="US",
                phone=link.select_one("a.phone").text.strip(),
                locator_domain=locator_domain,
                latitude=coord[1],
                longitude=coord[0],
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
