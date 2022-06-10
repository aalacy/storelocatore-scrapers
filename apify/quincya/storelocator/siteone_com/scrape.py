import json

from bs4 import BeautifulSoup

from sglogging import sglog

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

log = sglog.SgLogSetup().get_logger(logger_name="siteone.com")


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "siteone.com"

    found = []
    for i in range(100):
        base_link = (
            "https://www.siteone.com/store-finder?q=60101&miles=3000&page=%s" % i
        )
        log.info(base_link)
        try:
            stores = session.get(base_link, headers=headers).json()["data"]
        except:
            break

        for store in stores:
            location_name = store["name"]
            street_address = (store["line1"] + " " + store["line2"]).strip()
            city = store["town"]
            state = store["regionCode"]
            zip_code = store["postalCode"]
            country_code = "US"
            store_number = store["storeId"]
            location_type = "<MISSING>"
            phone = store["phone"]

            hours = store["openings"]
            hours_of_operation = ""
            for day in hours:
                hours_of_operation = (
                    hours_of_operation + " " + day + " " + hours[day]
                ).strip()
            if not hours_of_operation:
                hours_of_operation = "<MISSING>"

            latitude = store["latitude"]
            longitude = store["longitude"]

            link = "https://www.siteone.com/en/store/" + store_number
            found.append(link)

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

    if "https://www.siteone.com/en/store/396" not in found:
        link = "https://www.siteone.com/en/store/396"
        log.info(link)
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        script = base.find("script", attrs={"type": "application/ld+json"}).contents[0]
        store = json.loads(script)

        location_name = store["name"]
        street_address = store["address"]["streetAddress"]
        city = store["address"]["addressLocality"]
        state = store["address"]["addressRegion"]
        zip_code = store["address"]["postalCode"]
        store_number = location_name.split("#")[-1]
        phone = store["address"]["telephone"]

        hours_of_operation = ""
        raw_hours = store["openingHoursSpecification"]
        for hours in raw_hours:
            day = hours["dayOfWeek"]
            opens = hours["opens"]
            closes = hours["closes"]
            if opens != "" and closes != "":
                clean_hours = day + " " + opens + "-" + closes
                hours_of_operation = (hours_of_operation + " " + clean_hours).strip()

        if "sat" not in hours_of_operation.lower():
            hours_of_operation = hours_of_operation + " SATURDAY CLOSED"

        if "sun" not in hours_of_operation.lower():
            hours_of_operation = hours_of_operation + " SUNDAY CLOSED"

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
