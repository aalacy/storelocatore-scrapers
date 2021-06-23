from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
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


logger = SgLogSetup().get_logger("macallisterrentals")

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.macallisterrentals.com"
    base_url = "https://www.macallisterrentals.com/about/locations/"
    with SgRequests() as session:
        links = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("mapp.data.push(")[1]
            .split("if (typeof")[0]
            .strip()[:-2]
        )["pois"]
        logger.info(f"{len(links)} found")
        with SgChrome() as driver:
            for link in links:
                page_url = bs(link["body"], "lxml").a["href"]
                if not page_url.startswith("http"):
                    page_url = locator_domain + page_url
                logger.info(page_url)
                driver.get(page_url)
                sp1 = bs(driver.page_source, "lxml")
                ss = json.loads(
                    sp1.find_all("script", type="application/ld+json")[-1].string
                )
                hours = []
                if ss.get("openingHoursSpecification"):
                    hours = f"{','.join(ss['openingHoursSpecification']['dayOfWeek'])}: {ss['openingHoursSpecification']['opens']}-{ss['openingHoursSpecification']['closes']}"
                yield SgRecord(
                    page_url=page_url,
                    location_name=link["title"],
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


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
