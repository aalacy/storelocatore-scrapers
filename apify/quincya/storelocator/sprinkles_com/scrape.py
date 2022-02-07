from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("sprinkles_com")


def fetch_data(sgw: SgWriter):

    base_link = "https://sprinkles.com/pages/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.main.find_all(class_="item")

    for item in items:
        locator_domain = "sprinkles.com"

        location_name = item.h3.text.strip()
        logger.info(location_name)

        raw_address = list(item.p.stripped_strings)
        if raw_address[0] == "Houston, TX":
            continue
        if "coming soon" in str(raw_address).lower():
            continue
        street_address = " ".join(raw_address[:-2]).strip()
        try:
            city_line = raw_address[-2].strip().split(",")
        except:
            street_address = raw_address[0].split(",")[0]
            city_line = ",".join(raw_address[0].split(",")[1:]).strip().split(",")
        if not street_address:
            street_address = raw_address[0].strip()
            city_line = raw_address[1].strip().split(",")
        if "Las Vegas," in street_address:
            street_address = ""
            city_line = raw_address[0].strip().split(",")
        if "Amherst" in str(city_line):
            street_address = raw_address[-2].strip()
            city_line = raw_address[-1].strip().split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = item.find(class_="tel").text.strip()
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = ""

        page_link = "https://sprinkles.com" + item.a["href"]
        page_req = session.get(page_link, headers=headers)

        if page_req.status_code != 404:
            page = BeautifulSoup(page_req.text, "lxml")

            try:
                location_type = ",".join(
                    list(page.find(class_="order-buttons").stripped_strings)
                )
            except:
                location_type = ""

            raw_hours = page.find(class_="addr-hours")
            raw_hours = raw_hours.find_all("p")

            for hour in raw_hours:
                if "hours" in hour.text.lower():
                    hours_of_operation = (
                        " ".join(list(hour.stripped_strings))
                        .split("hours:")[1]
                        .split("The hours above")[0]
                        .replace("The SIMON Fashion Valley Mall ATM is open", "")
                        .replace("Hollywood & Highland ATM is open", "")
                        .strip()
                    )
        else:
            page_link = base_link

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=page_link,
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


with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))) as writer:
    fetch_data(writer)
