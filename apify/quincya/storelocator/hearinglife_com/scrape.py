import re

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://www.hearinglife.com/api/clinics/getclinics/%7B04A27535-671F-4E6B-80C3-75F3CE5DC685%7D"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()

    locator_domain = "https://www.hearinglife.com"

    for store in stores:
        location_name = store["Name"]

        raw_address = store["Address"]
        street_address = (
            raw_address.split(", " + location_name.split("-")[0].strip())[0]
            .split("(")[0]
            .strip()
        )

        city = location_name.split(",")[0].strip()
        state = store["Region"].replace("-", " ")
        zip_code = raw_address.split()[-1]

        if zip_code in street_address:
            raw_address = (
                store["Address"]
                .replace("St Modesto", "St, Modesto")
                .replace("7 Turlock", "7, Turlock")
                .split(",")
            )
            if len(raw_address) < 5:
                street_address = ",".join(raw_address[:-2])
                city = raw_address[-2].strip()
            elif len(raw_address) == 5:
                street_address = ",".join(raw_address[:-3])
                city = raw_address[-3].strip()
            else:
                raise

        if re.search(r"\d", street_address):
            digit = str(re.search(r"\d", street_address))
            start = int(digit.split("(")[1].split(",")[0])
            street_address = street_address[start:]

        if street_address[-1:] == ",":
            street_address = street_address[:-1].strip()

        if len(zip_code) == 4:
            zip_code = "0" + zip_code

        street_address = street_address.split(", TJ Maxx")[0]
        city = city.split("Spring Vall")[0].split("-")[0].strip()

        country_code = "US"
        location_type = ""
        phone = store["PhoneNumber"]
        hours_of_operation = ""
        raw_hours = store["BusinessHours"]
        for raw_hour in raw_hours:
            hours_of_operation = (
                hours_of_operation
                + " "
                + raw_hour["DayName"]
                + " "
                + raw_hour["DayHours"]
            ).strip()
        latitude = store["Latitude"]
        longitude = store["Longitude"]
        store_number = store["ClinicId"]
        link = locator_domain + store["ItemUrl"]

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
