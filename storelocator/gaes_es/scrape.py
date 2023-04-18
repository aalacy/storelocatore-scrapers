from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
import json
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("gaes")

locator_domain = "https://www.gaes.es"
base_url = "https://www.gaes.es/nuestros-centros-auditivos"
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetch_data():
    locations = []
    with SgChrome(
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"
    ) as driver:
        driver.get(base_url)
        urls = (
            bs(driver.page_source, "lxml")
            .select("div.richtext-container p")[1]
            .select("a")
        )
        for url in urls:
            logger.info(locator_domain + url["href"])
            driver.get(locator_domain + url["href"])
            locations += [
                loc
                for loc in bs(driver.page_source, "lxml").select("div.m-store-teaser")
            ]

        logger.info(f"{len(locations)} locations")
        for loc in locations:
            page_url = loc.a["href"]
            logger.info(f"[***] {page_url}")
            driver.get(page_url)
            sp1 = bs(driver.page_source, "lxml")
            if driver.current_url == base_url:
                continue
            try:
                _ = json.loads(sp1.find("script", type="application/ld+json").string)
            except:
                addr = loc.p.text.strip().split(",")
                yield SgRecord(
                    page_url=page_url,
                    location_name=loc.span.text.strip(),
                    locator_domain=locator_domain,
                    street_address=" ".join(addr[:-2]),
                    city=addr[-1].split("/")[0],
                    zip_postal=addr[-2],
                    country_code="Spain",
                )
                continue
            phone = ""
            if sp1.select_one("span.phone-list"):
                phone = sp1.select_one("span.phone-list").text.split("/")[0].strip()
            hours = []
            temp = {}
            if _.get("openingHoursSpecification"):
                for hh in _["openingHoursSpecification"]:
                    day = hh["dayOfWeek"]
                    if not temp.get(day):
                        temp[day] = []
                    temp[day].append(f"{hh['opens']} - {hh['closes']}")
            for day in days:
                if temp.get(day):
                    hours.append(f"{day}: {' | '.join(temp[day])}")
                else:
                    hours.append(f"{day}: Closed")
            addr = _["address"]
            yield SgRecord(
                page_url=page_url,
                store_number=_["branchCode"],
                location_name=_["name"],
                street_address=addr["streetAddress"],
                city=addr["addressLocality"],
                state=addr["addressRegion"],
                zip_postal=addr["postalCode"],
                latitude=_["geo"]["latitude"],
                longitude=_["geo"]["longitude"],
                country_code="Spain",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
