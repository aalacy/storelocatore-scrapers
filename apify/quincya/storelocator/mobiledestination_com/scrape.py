import json

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("mobiledestination_com")


def fetch_data(sgw: SgWriter):

    base_link = "https://www.mobiledestination.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="city-name")
    locator_domain = "mobiledestination.com"

    for item in items:

        link = "https://www.mobiledestination.com" + item.a["href"]

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.h1.text.strip()
        logger.info(link)
        script = base.find_all("script", attrs={"type": "application/ld+json"})[
            -1
        ].contents[0]
        store = json.loads(script)

        street_address = store["address"]["streetAddress"].replace("&#39;", "'")
        city = store["address"]["addressLocality"]
        state = store["address"]["addressRegion"]
        zip_code = store["address"]["postalCode"]
        country_code = store["address"]["addressCountry"]["name"]
        store_number = link.split("locations/")[1].split("/")[0]
        location_type = "<MISSING>"

        try:
            phone = store["telephone"]
        except:
            phone = ""

        hours_of_operation = " ".join(
            list(base.find(class_="store-hours").ul.stripped_strings)
        )

        try:
            latitude = store["geo"]["latitude"].strip()
            longitude = store["geo"]["longitude"].strip()
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=link,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state.strip(),
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
