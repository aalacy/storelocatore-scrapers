from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("jakesfireworks")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.jakesfireworks.com"
base_url = "https://www.jakesfireworks.com/stores"


def fetch_data():
    with SgRequests(verify_ssl=False) as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.views-row")
        for _ in locations:
            page_url = locator_domain + _.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            raw_address = (
                " ".join(_.select_one("p.address").stripped_strings)
                .replace("Jakes Fireworks,", "")
                .strip()
            )
            street_address = _.select_one("span.address-line1").text.strip()
            if _.select_one("span.address-line2"):
                street_address += " " + _.select_one("span.address-line2").text.strip()
            phone = ""
            _p = _.select_one("div.views-field-field-telephone-number a")
            if _p:
                phone = _p.text.strip()
            _hr = sp1.find("h3", string=re.compile(r"Hours of Operation"))
            hours = ""
            if _hr:
                hours = " ".join(list(_hr.find_parent().stripped_strings)[1:])
            if hours and "is closed" in hours.lower():
                hours = "temporarily closed"
            yield SgRecord(
                page_url=page_url,
                location_name=_.h2.text.strip(),
                street_address=street_address.replace("Jakes Fireworks,", "").strip(),
                city=_.select_one("span.locality").text.strip(),
                state=_.select_one("span.administrative-area").text.strip(),
                zip_postal=_.select_one("span.postal-code").text.strip(),
                country_code="US",
                phone=phone,
                latitude=sp1.select_one('meta[itemprop="latitude"]')["content"],
                longitude=sp1.select_one('meta[itemprop="longitude"]')["content"],
                locator_domain=locator_domain,
                hours_of_operation=hours,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
