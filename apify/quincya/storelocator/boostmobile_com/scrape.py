import json
import os

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("boostmobile_com")


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    proxy_password = os.environ["PROXY_PASSWORD"]
    proxy_url = "http://groups-RESIDENTIAL,country-US:{}@proxy.apify.com:8000/".format(
        proxy_password
    )
    proxies = {"http": proxy_url, "https": proxy_url}
    session.proxies = proxies

    base_link = "https://www.boostmobile.com/locations/"
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    all_links = []

    locator_domain = "https://www.boostmobile.com"

    items = base.find_all(class_="lm-homepage__state")

    for i in items:
        link = locator_domain + i["href"]
        logger.info(link)
        try:
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
        except:
            session = SgRequests()
            session.proxies = proxies
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

        locs = base.find_all(class_="lm-state__store")
        for loc in locs:
            all_links.append(locator_domain + loc["href"])

    num = 1
    for link in all_links:
        if num % 20 == 0:
            session = SgRequests()
            session.proxies = proxies
        num = num + 1
        try:
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
        except:
            logger.info(link)
            session = SgRequests()
            session.proxies = proxies
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

        script = base.find("script", attrs={"type": "application/ld+json"}).contents[0]
        store = json.loads(script)
        location_name = store["name"]
        street_address = store["address"]["streetAddress"]
        city = store["location"]["address"]["addressLocality"]
        state = store["location"]["address"]["addressRegion"]
        zip_code = store["location"]["address"]["postalCode"]
        country_code = "US"
        store_number = store["branchCode"]
        location_type = store["@type"]
        phone = store["telephone"]
        try:
            hours_of_operation = " ".join(store["openingHoursSpecification"])
        except:
            hours_of_operation = ""
        if not hours_of_operation:
            try:
                if (
                    "opening soon"
                    in base.find(
                        class_="lm-list-item__details lm-grid__flex"
                    ).text.lower()
                ):
                    hours_of_operation = "Opening Soon"
            except:
                pass

        latitude = store["geo"]["latitude"]
        longitude = store["geo"]["longitude"]

        if city in street_address:
            street_address = street_address[: street_address.rfind(city)].strip()

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
