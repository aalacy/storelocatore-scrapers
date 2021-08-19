from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import re
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("thenomadhotel")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://thenomadhotel.com/"
base_url = "https://www.thenomadhotel.com"
url1 = "https://www.thenomadhotel.com/contact/"


def fetch_data(
    user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
):
    with SgChrome() as driver:
        driver.get(url1)
        all_locs = bs(driver.page_source, "lxml").select("div#all section.contact-info")
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
                    street_address=sp1.address.text.strip(),
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
                for loc in all_locs:
                    addr = list(
                        loc.select_one("div.col-md-4")
                        .findChildren(recursive=False)[0]
                        .stripped_strings
                    )
                    if link.text.strip() in addr[1]:
                        yield SgRecord(
                            page_url=page_url,
                            location_name=loc.h2.text.strip(),
                            street_address=addr[0],
                            city=link.text.strip(),
                            state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                            zip_postal=addr[1]
                            .split(",")[1]
                            .strip()
                            .split(" ")[-1]
                            .strip(),
                            country_code="US",
                            phone=sp1.select_one(
                                "div.detail_content div a"
                            ).text.strip(),
                            locator_domain=locator_domain,
                        )
                        break


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
