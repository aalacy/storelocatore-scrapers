import json
import time

from bs4 import BeautifulSoup

from sglogging import sglog

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

log = sglog.SgLogSetup().get_logger("frysfood.com")


def fetch_data(sgw: SgWriter):

    base_link = "https://www.kingsoopers.com/storelocator-sitemap.xml"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all("loc")

    locator_domain = "https://www.kingsoopers.com"

    for item in items:
        link = item.text
        if "stores/search" not in link:
            log.info(link)
            try:
                req = session.get(link, headers=headers)
                base = BeautifulSoup(req.text, "lxml")
                script = base.find(
                    "script", attrs={"type": "application/ld+json"}
                ).contents[0]
            except:
                try:
                    time.sleep(5)
                    log.info("Retrying ..")
                    session = SgRequests()
                    time.sleep(4)
                    req = session.get(link, headers=headers)
                    base = BeautifulSoup(req.text, "lxml")
                    script = base.find(
                        "script", attrs={"type": "application/ld+json"}
                    ).contents[0]
                except:
                    log.info("Retrying ..")
                    time.sleep(10)
                    session = SgRequests()
                    time.sleep(10)
                    req = session.get(link, headers=headers)
                    base = BeautifulSoup(req.text, "lxml")
                    script = base.find(
                        "script", attrs={"type": "application/ld+json"}
                    ).contents[0]

            store = json.loads(script)

            location_name = base.find(
                "h1", {"data-qa": "storeDetailsHeader"}
            ).text.strip()

            deps = store["department"]
            for dep in deps:
                if dep["@type"] == "Pharmacy":
                    try:
                        street_address = store["address"]["streetAddress"]
                        city = store["address"]["addressLocality"]
                        state = store["address"]["addressRegion"]
                        zip_code = store["address"]["postalCode"]
                    except:
                        raw_address = (
                            base.find(class_="StoreAddress-storeAddressGuts")
                            .get_text(" ")
                            .replace("7915  ", "7915 ")
                            .replace(",", "")
                            .replace(" .", ".")
                            .replace("..", ".")
                            .split("  ")
                        )
                        street_address = raw_address[0].strip()
                        city = raw_address[1].strip()
                        state = raw_address[2].strip()
                        zip_code = raw_address[3].split("Get")[0].strip()

                    country_code = "US"
                    store_number = link.split("/")[-1]
                    location_type = "<MISSING>"
                    phone = dep["telephone"]
                    hours_of_operation = (
                        " ".join(dep["openingHours"])
                        .replace("Su-Sa", "Sun - Sat:")
                        .replace("Su-Fr", "Sun - Fri:")
                        .replace("-00:00", " - Midnight")
                        .replace("Su ", "Sun")
                        .replace("Mo-Fr", "Mon - Fri")
                        .replace("Sa ", "Sat ")
                        .replace("  ", " ")
                    ).strip()
                    latitude = store["geo"]["latitude"]
                    longitude = store["geo"]["longitude"]

                    sgw.write_row(
                        SgRecord(
                            locator_domain=locator_domain,
                            page_url=link,
                            location_name=location_name,
                            street_address=street_address,
                            city=city,
                            state=state,
                            zip_postal=zip_code,
                            country_code=country_code,
                            store_number=store_number,
                            phone=phone,
                            location_type=location_type,
                            latitude=latitude,
                            longitude=longitude,
                            hours_of_operation=hours_of_operation,
                        )
                    )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
