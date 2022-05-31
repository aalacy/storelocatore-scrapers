import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("nandos_co_uk")


def fetch_data(sgw: SgWriter):

    base_link = "https://www.nandos.co.uk/restaurants/all"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="accordion-a11ly__rest-item")
    locator_domain = "nandos.co.uk"

    for i, item in enumerate(items):
        logger.info("Link %s of %s" % (i + 1, len(items)))
        link = "https://www.nandos.co.uk" + item.a["href"]
        logger.info(link)

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        script = base.find("script", attrs={"type": "application/ld+json"}).contents[0]
        store = json.loads(script)

        location_name = store["name"]
        street_address = store["address"]["streetAddress"].strip().replace("amp;", "")
        city = store["address"]["addressLocality"]
        state = store["address"]["addressRegion"]

        if "Dublin" in state or state == "County Kildare" or state == "Cork":
            continue
        zip_code = store["address"]["postalCode"]
        if not zip_code:
            zip_code = "<MISSING>"
        country_code = "GB"

        if zip_code in street_address:
            street_address = street_address.replace(", " + zip_code, "")
        if street_address[-1:] == ",":
            street_address = street_address[:-1]

        if not city:
            city = street_address.split(",")[-1].strip()
            street_address = street_address[: street_address.rfind(",")]

        if not state:
            if city in ["London", "Merseyside"]:
                state = city

        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = store["contactPoint"][0]["telephone"]
        if phone == "+44":
            phone = "<MISSING>"
        hours_of_operation = (
            store["openingHours"][0]
            .replace("CLOSED", "Closed")
            .replace("Closed-Closed", "Closed")
            .replace("-Closed", "Closed")
            .strip()
        )
        if hours_of_operation == "mo-su -":
            hours_of_operation = "<MISSING>"

        latitude = store["geo"]["latitude"]
        longitude = store["geo"]["longitude"]
        if not latitude:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        if "Blanchardstown Rd S" in street_address:
            latitude = "53.3917382"
            longitude = "-6.3979187"

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
