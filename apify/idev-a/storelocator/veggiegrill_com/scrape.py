from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgselenium import SgChrome
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import ssl
import re

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

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
            locations = bs(driver.page_source, "lxml").select(
                "div.accordions .location-sm"
            )
            for location in locations:
                addr = list(location.select_one("address").stripped_strings)
                phone = location.find("a", href=re.compile("tel:")).text.strip()
                page_url = base_url
                hours = []
                coord = ["<INACCESIBLE>", "<INACCESIBLE>"]
                if location.select("a.btn"):
                    page_url = location.select("a.btn")[-1]["href"]
                    logger.info(page_url)
                    soup1 = bs(session.get(page_url, headers=_headers()).text, "lxml")
                    try:
                        coord = (
                            soup1.address.find_next_sibling("a")["href"]
                            .split("/@")[1]
                            .split("/data")[0]
                            .split(",")
                        )
                    except:
                        coord = ["<INACCESIBLE>", "<INACCESIBLE>"]

                    labels = [_.text for _ in soup1.select("dl.hours dt")]
                    values = [_.text.strip() for _ in soup1.select("dl.hours dd")]
                    for x in range(len(labels)):
                        hours.append(f"{labels[x]}: {values[x]}")
                street_address = (
                    " ".join(addr[:-1]).replace("Ackerman Student Union", "").strip()
                )
                if street_address.endswith(","):
                    street_address = street_address[:-1]
                yield SgRecord(
                    page_url=page_url,
                    store_number=location["id"],
                    location_name=location.b.text.strip(),
                    street_address=street_address,
                    city=addr[-1].split(",")[0].strip(),
                    state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                    zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                    country_code="US",
                    phone=phone,
                    latitude=coord[0],
                    longitude=coord[1],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    raw_address=" ".join(addr).replace("Ackerman Student Union", ""),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
