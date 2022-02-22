from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("hcrcenters")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.hcrcenters.com/"
base_url = "https://www.hcrcenters.com/our-location/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.our-location-info-blocks li.location-link")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            ss = json.loads(
                sp1.find_all("script", type="application/ld+json")[-1].string.strip()
            )
            try:
                coord = ss["hasMap"].split("/@")[1].split("/data")[0].split(",")
            except:
                coord = (
                    sp1.select_one(".responsive-map iframe")["data-lazy-src"]
                    .split("!2d")[1]
                    .split("!2m")[0]
                    .split("!3d")[::-1]
                )
            hours = []
            temp = list(sp1.select_one("div.sidebar-info-time").stripped_strings)
            for hh in temp[1:]:
                if "treatment center hours" in hh.lower():
                    continue
                if "medication hours" in hh.lower():
                    break
                hours.append(hh)
            yield SgRecord(
                page_url=page_url,
                location_name=" ".join(bs(ss["name"], "lxml").stripped_strings),
                street_address=ss["address"]["streetAddress"],
                city=ss["address"]["addressLocality"],
                state=ss["address"]["addressRegion"],
                zip_postal=ss["address"]["postalCode"],
                country_code="US",
                phone=ss["telephone"],
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
