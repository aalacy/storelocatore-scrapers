import csv
import re

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://www.hearinglife.ca/api/clinics/getclinics/%7B18ED6344-6000-467C-97A8-31D51DAFD2E0%7D"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()

    locator_domain = "hearinglife.ca"

    cities = []
    city_file = csv.reader(open("canada_list.csv", "r"), delimiter=",", quotechar='"')
    for row in city_file:
        city_name = str(row[0]).strip()
        cities.append(city_name)

    for store in stores:
        location_name = store["Name"]

        raw_address = store["Address"]
        street_address = (
            "".join(raw_address.split(",")[:-1])
            .replace("4 (PO Box 97)", "")
            .replace("Alpha Corporate Centre -", "")
            .split("(")[0]
            .replace("â€™", "'")
        )
        if "|" in street_address:
            street_address = street_address.split("|")[1].strip()
        if " - " in street_address[15:]:
            street_address = street_address[: street_address.rfind("-")]

        state = store["Region"].replace("-", " ").title()
        if "Newfoundland" in state:
            state = "Newfoundland and Labrador"
        zip_code = raw_address.split(",")[-1]

        city = ""
        for city_name in cities:
            if city_name in location_name:
                city = city_name
                if city == "Lang":
                    city = "Langley"
                break

        if len(zip_code) > 10:
            street_address = " ".join(zip_code.split()[:-3])
            zip_code = " ".join(zip_code.split()[-3:-1])
        if zip_code in street_address:
            street_address = street_address.replace(zip_code, "").strip()

        if re.search(r"\d", street_address):
            digit = str(re.search(r"\d", street_address))
            start = int(digit.split("(")[1].split(",")[0])
            street_address = street_address[start:]

        if street_address[-1:] == ",":
            street_address = street_address[:-1].strip()

        country_code = "CA"
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
        hours_of_operation = hours_of_operation.replace("<!-- ", "").replace(" -->", "")
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
