from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgselenium import SgChrome
import re
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("veggiegrill")


locator_domain = "https://veggiegrill.com/"
base_url = "https://veggiegrill.com/locations/"


def _headers():
    return {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "en-US,en;q=0.9,ko;q=0.8",
        "referer": "https://veggiegrill.com/",
        "cache-control": "max-age=0",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    }


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        with SgRequests() as session:
            session.get(locator_domain, headers=_headers())
            locations = bs(driver.page_source, "html.parser").select(
                "div.accordions .location-sm"
            )
            for location in locations:
                addr = list(location.select_one("address").stripped_strings)
                phone = location.find("a", href=re.compile("tel:")).text.strip()
                page_url = location.select("a.btn")[-1]["href"]
                logger.info(page_url)
                soup1 = bs(session.get(page_url, headers=_headers()).text, "lxml")
                labels = [_.text for _ in soup1.select("dl.hours dt")]
                values = [_.text.strip() for _ in soup1.select("dl.hours dd")]
                hours = []
                for x in range(len(labels)):
                    hours.append(f"{labels[x]}: {values[x]}")

                yield SgRecord(
                    page_url=page_url,
                    store_number=location["id"],
                    location_name=location.b.text.strip(),
                    street_address=" ".join(addr[:-1]),
                    city=addr[-1].split(",")[0].strip(),
                    state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                    zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                    country_code="US",
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    raw_address=" ".join(addr),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
