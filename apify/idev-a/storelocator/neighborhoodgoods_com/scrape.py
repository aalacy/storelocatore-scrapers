from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("neighborhoodgoods")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://neighborhoodgoods.com"
    base_url = "https://neighborhoodgoods.com/pages/locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select(
            "div.view-page-locations div.shopify-section div.two-up div.content-wrapper a"
        )
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            raw_address = sp1.select_one("div.content p a").text.strip()
            addr = raw_address.split(",")
            temp = list(
                sp1.find("h3", string=re.compile(r"^Hours"))
                .find_next_sibling()
                .stripped_strings
            )
            hours = []
            for hh in temp:
                if "location" in hh:
                    break
                hours.append(hh)
            phone = ""
            if sp1.find("a", href=re.compile(r"tel:")):
                phone = sp1.find("a", href=re.compile(r"tel:")).text.strip()
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.select_one("div.content h3").text.strip(),
                street_address=" ".join(addr[:-2]),
                city=addr[-2],
                state=addr[-1].strip().split()[0],
                zip_postal=addr[-1].strip().split()[-1],
                country_code="US",
                phone=phone.replace("(", "").replace(")", ""),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
