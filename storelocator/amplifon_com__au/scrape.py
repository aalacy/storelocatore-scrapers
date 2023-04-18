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
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetch_data():
    locations = []
    with SgRequests() as http:
        urls = bs(http.get(base_url, headers=_headers).text, "lxml").select("url loc")
        for url in urls:
            _url = url.text
            if (
                "au/audiologist-hearing-test-clinics/" in _url
                and len(_url.split("/")) == 6
            ):
                locations.append(_url)

        logger.info(f"{len(locations)} locations")
        for url in locations:
            logger.info(f"[***] {url}")
            locs = bs(http.get(url, headers=_headers).text, "lxml").select(
                "div.richtext-container ul li a"
            )
            for loc in locs:
                if not loc.get("href"):
                    continue
                page_url = loc["href"]
                logger.info(f"[***] {page_url}")
                res = http.get(page_url, headers=_headers)
                if res.status_code != 200:
                    continue
                sp1 = bs(res.text, "lxml")
                _ = json.loads(sp1.find("script", type="application/ld+json").string)
                phone = ""
                if sp1.select_one("span.phone-list"):
                    phone = sp1.select_one("span.phone-list").text.strip()
                hours = []
                temp = {}
                for hh in _["openingHoursSpecification"]:
                    day = hh["dayOfWeek"]
                    temp[day] = f"{hh['opens']} - {hh['closes']}"
                for day in days:
                    if temp.get(day):
                        hours.append(f"{day}: {temp[day]}")
                    else:
                        hours.append(f"{day}: closed")
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
