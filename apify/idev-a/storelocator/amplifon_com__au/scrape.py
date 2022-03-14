from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("gaes")

locator_domain = "https://www.amplifon.com/au/"
base_url = "https://www.amplifon.com/au/sitemap.xml"

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locations = []
    with SgRequests() as http:
        urls = bs(http.get(base_url, headers=_headers).text, "lxml").select("loc")
        for url in urls:
            _url = url.text
            if (
                "au/audiologist-hearing-test-clinics/" not in _url
                or len(_url.split("/")) < 7
            ):
                continue
            locations.append(_url)

        logger.info(f"{len(locations)} locations")
        for page_url in locations:
            logger.info(f"[***] {page_url}")
            sp1 = bs(http.get(page_url, headers=_headers).text, "lxml")
            _ = json.loads(sp1.find("script", type="application/ld+json").string)
            phone = ""
            if sp1.select_one("span.phone-list"):
                phone = sp1.select_one("span.phone-list").text.strip()
            hours = []
            for hh in _["openingHoursSpecification"]:
                day = hh["dayOfWeek"]
                hours.append(f"{day}: {hh['opens']} - {hh['closes']}")
            addr = _["address"]
            street_address = addr["streetAddress"].strip()
            if street_address.endswith(","):
                street_address = street_address[:-1]
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                street_address=street_address,
                city=addr["addressLocality"],
                state=addr.get("addressRegion"),
                zip_postal=addr.get("postalCode"),
                latitude=_["geo"]["latitude"],
                longitude=_["geo"]["longitude"],
                country_code="Australia",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
