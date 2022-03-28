from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from urllib.parse import urljoin

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.citymd.com"
base_url = "https://www.citymd.com/all-locations"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.question-list a.link-btn")
        
        for link in links:
            page_url = urljoin(locator_domain, link["href"])
            logger.info(page_url)
            res = session.get(page_url, headers=_headers)
            sp1 = bs(res.text, "lxml")
            raw_address = sp1.h1.find_next_sibling().p.text.strip()
            addr = raw_address.split(",")
            phone = ""
            if sp1.select_one("a.location-phone-number"):
                phone = sp1.select_one("a.location-phone-number").text.strip()
            latlng = (
                sp1.select_one("a.directions-link")["href"].split("/@")[1].split(",")
            )
            hours = []
            if sp1.select_one("div.hours-message-container"):
                for hh in sp1.select_one(
                    "div.hours-message-container"
                ).find_next_siblings("p"):
                    if "Read" in hh.text:
                        break
                    hours.append(": ".join(hh.stripped_strings))
            yield SgRecord(
                page_url=res.url.__str__(),
                location_name=sp1.h1.text.strip(),
                street_address=" ".join(addr[:-2]),
                city=addr[-2].strip(),
                state=addr[-1].strip().split()[0].strip(),
                zip_postal=addr[-1].strip().split()[-1].strip(),
                country_code="USA",
                phone=phone,
                latitude=latlng[0],
                longitude=latlng[1].split("@")[-1],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
