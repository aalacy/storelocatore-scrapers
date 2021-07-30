from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import re

logger = SgLogSetup().get_logger("thenomadhotel")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://thenomadhotel.com/"
base_url = "https://thenomadhotel.com/"


def fetch_data(
    user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
):
    with SgChrome() as driver:
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        links = soup.select("div.nav-bar.js-sticky nav.nav a.nav-item.nav-link")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link["href"]
            logger.info(page_url)
            driver.get(page_url)
            sp1 = bs(driver.page_source, "lxml")
            try:
                ss = json.loads(
                    sp1.find("script", string=re.compile(r"latitude")).string
                )
                hours = f"{','.join(ss['openingHoursSpecification']['dayOfWeek'])}: {ss['openingHoursSpecification']['opens']}-{ss['openingHoursSpecification']['closes']}"
                yield SgRecord(
                    page_url=page_url,
                    location_name=ss["name"],
                    street_address=ss["address"]["streetAddress"],
                    city=ss["address"]["addressLocality"],
                    state=ss["address"]["addressRegion"],
                    zip_postal=ss["address"]["postalCode"],
                    country_code=ss["address"]["addressCountry"],
                    phone=ss["telephone"],
                    locator_domain=locator_domain,
                    latitude=ss["geo"]["latitude"],
                    longitude=ss["geo"]["longitude"],
                    hours_of_operation=hours,
                )
            except:
                yield SgRecord(
                    page_url=page_url,
                    location_name=link.text.strip(),
                    street_address=sp1.select_one(
                        "div.detail_content address"
                    ).text.strip(),
                    city=link.text.strip(),
                    country_code="US",
                    phone=sp1.select_one("div.detail_content div a").text.strip(),
                    locator_domain=locator_domain,
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
