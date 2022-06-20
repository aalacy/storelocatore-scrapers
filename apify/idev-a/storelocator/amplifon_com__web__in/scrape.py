from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
import re

logger = SgLogSetup().get_logger("gaes")


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.amplifon.com"
in_url = "https://www.amplifon.com/in/store-locator"
hu_url = "https://www.amplifon.com/hu/sitemap.xml"
pl_url = "https://www.amplifon.com/pl/sitemap.xml"


def fetch_others():
    with SgRequests() as session:
        urls = {}
        urls["in"] = []
        for loc in (
            bs(session.get(in_url, headers=_headers).text, "xml")
            .find("h3", string=re.compile(r"Search by area"))
            .find_next_sibling()
            .select("li a")
        ):
            url = locator_domain + loc["href"]
            logger.info(url)
            locations = bs(session.get(url, headers=_headers).text, "xml").select(
                "div.m-store-teaser a.d-block"
            )
            for _ in locations:
                urls["in"].append(_["href"])
        urls["hu"] = [
            loc.text
            for loc in bs(session.get(hu_url, headers=_headers).text, "lxml").select(
                "loc"
            )
        ]
        urls["pl"] = [
            loc.text
            for loc in bs(session.get(pl_url, headers=_headers).text, "lxml").select(
                "loc"
            )
        ]
        for country, url1 in urls.items():
            for page_url in url1:
                if (
                    "pl/nasze-gabinety/" not in page_url
                    and "hu/hallaskozpont-kereso/" not in page_url
                    and "in/store-locator/" not in page_url
                ):
                    continue

                if len(page_url.split("/")) < 7:
                    continue

                if "store-detail" in page_url:
                    continue

                logger.info(f"[***] {page_url}")
                sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                _ = json.loads(sp1.find("script", type="application/ld+json").string)
                phone = ""
                if sp1.select_one("span.phone-list"):
                    try:
                        phone = list(
                            sp1.select_one("span.phone-list").stripped_strings
                        )[0]
                    except:
                        pass
                hours = []
                for hh in _["openingHoursSpecification"]:
                    day = hh["dayOfWeek"]
                    hours.append(f"{day}: {hh['opens']} - {hh['closes']}")
                addr = _["address"]
                state = addr.get("addressRegion")
                if (
                    state.replace("(", "")
                    .replace(")", "")
                    .replace(" ", "")
                    .strip()
                    .isdigit()
                ):
                    state = ""
                yield SgRecord(
                    page_url=page_url,
                    location_name=_["name"],
                    street_address=addr["streetAddress"],
                    city=addr["addressLocality"],
                    state=state,
                    zip_postal=addr.get("postalCode"),
                    latitude=_["geo"]["latitude"],
                    longitude=_["geo"]["longitude"],
                    country_code=country,
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_others()
        for rec in results:
            writer.write_row(rec)
