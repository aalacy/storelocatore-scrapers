from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from bs4 import BeautifulSoup as bs
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.villagemedical.com"
base_url = "https://www.villagemedical.com/sitemap.xml"


def fetch_data():
    with SgRequests() as session:
        locations = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "loc"
        )
        for loc in locations:
            page_url = loc.text.strip()
            if "locations/" not in page_url or len(page_url.split("/")) < 6:
                continue
            logger.info(page_url)
            res = session.get(page_url, headers=_headers).text
            sp1 = bs(res, "lxml")
            try:
                _ = json.loads(sp1.find("script", type="application/ld+json").text)
            except:
                continue
            addr = _["address"]
            try:
                latlng = json.loads(res.split("const uluru =")[1].split(";")[0])
            except:
                latlng = {"lat": "", "lng": ""}
            hours = []
            hr = sp1.find("h3", string=re.compile(r"^Hours"))
            if hr:
                for hh in hr.find_next_siblings("div"):
                    hours.append(": ".join(hh.stripped_strings))
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"].replace("–", "-"),
                street_address=addr["streetAddress"],
                city=addr["addressLocality"],
                state=addr["addressRegion"],
                zip_postal=addr["postalCode"],
                country_code="US",
                phone=_["telephone"],
                locator_domain=locator_domain,
                latitude=latlng["lat"],
                longitude=latlng["lng"],
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
