from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("theuppercrustpizzeria")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.theuppercrustpizzeria.com"
base_url = "https://www.theuppercrustpizzeria.com/locations/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.location")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = base_url + "#" + link["id"]
            block = list(link.p.stripped_strings)
            addr = block[0].split(",")
            phone = ""
            if len(block) > 1:
                phone = block[1].split("at")[-1]
            yield SgRecord(
                page_url=page_url,
                location_name=link.strong.text.strip(),
                street_address=addr[0].replace("We are on", "").strip(),
                city=addr[1].strip(),
                state=addr[2].strip().split(" ")[0].strip(),
                zip_postal=addr[2].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                raw_address=block[0].replace("We are on", "").strip(),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
