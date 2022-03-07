from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import dirtyjson
import re
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("millersfresh")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "http://www.eathomegrown.com"
    base_url = "http://www.eathomegrown.com/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("li#region-list ul li a")
        logger.info(f"{len(links)} found")
        for link in links:
            url = locator_domain + link["href"]
            sp1 = bs(session.get(url, headers=_headers).text, "lxml")
            scripts = sp1.find_all("script", string=re.compile(r"var phoneNumber;"))
            for script in scripts:
                phone = (
                    script.string.split("phoneNumber = ")[-1].split("}")[0].strip()[:-1]
                )
                _ = dirtyjson.loads(
                    script.string.split("storeData.items.push(")[1]
                    .split(");")[0]
                    .strip()
                    .replace("phoneNumber", phone)
                )
                street_address = _["street1"]
                if _["street2"]:
                    street_address += " " + _["street2"]
                hours = []
                for hh in _["hours"].split(". "):
                    if " on" in hh or "closing " in hh.lower() or "opens" in hh.lower():
                        break
                    hours.append(hh.replace("&amp;", "&").split("*")[0].strip())
                page_url = f"http://www.eathomegrown.com/locations?location={_['slug']}"
                yield SgRecord(
                    page_url=page_url,
                    location_name=_["storeName"].replace("&amp;", "&"),
                    street_address=street_address,
                    city=_["city"],
                    state=_["state"],
                    zip_postal=_["zip"],
                    country_code="US",
                    phone=_["phone"],
                    locator_domain=locator_domain,
                    latitude=_["lat"],
                    longitude=_["lng"],
                    hours_of_operation="; ".join(hours),
                )

            break


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
