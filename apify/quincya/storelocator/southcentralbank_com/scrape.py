import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.southcentralbank.com/wp-json/wpgmza/v1/features/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMoxR0gEJFGeUFni6FAPFomOBAsmlxSX5uW6ZqTkpELFapVoABU0Wug"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    store_data = session.get(base_link, headers=headers).json()["markers"]

    locator_domain = "southcentralbank.com"

    for store in store_data:
        location_name = store["title"].upper()
        if "ATM" in location_name:
            location_type = "ATM Location"
        elif "office" in location_name.lower() or "operations" in location_name.lower():
            location_type = "Office Location"
        else:
            location_type = "Loan Production Office"

        raw_data = BeautifulSoup(store["description"], "lxml")
        try:
            raw_address = list(raw_data.stripped_strings)[:2]
            if "LOCATION" in raw_address[0]:
                raw_address = list(raw_data.stripped_strings)[1:3]
        except:
            raw_address = store["address"]

        street_address = raw_address[0].strip()
        city = raw_address[1].split(",")[0]
        try:
            state = raw_address[1].split(",")[1].split()[0]
            zip_code = raw_address[1].split(",")[1].split()[1]
        except:
            raw_address = store["address"].split(",")
            street_address = raw_address[0].strip()
            city = raw_address[1].strip()
            state = raw_address[2].split()[0].strip()
            zip_code = raw_address[2].split()[1].strip()
        country_code = "US"
        store_number = store["id"]

        try:
            phone = re.findall(r"[(\d)]{3}-[\d]{3}-[\d]{4}", store["description"])[0]
        except:
            try:
                phone = re.findall(r"[(\d)]{5} [\d]{3}-[\d]{4}", store["description"])[
                    0
                ]
            except:
                phone = "<MISSING>"

        hours_of_operation = "<MISSING>"
        rows = list(raw_data.stripped_strings)
        for i, row in enumerate(rows):
            if "hours" in row.lower():
                hours_of_operation = (
                    " ".join(rows[i:])
                    .replace("ATM", "")
                    .strip()
                    .split("Drive")[0]
                    .split("Please")[0]
                    .strip()
                )
                break

        latitude = store["lat"]
        longitude = store["lng"]

        link = "https://www.southcentralbank.com/locations-and-team-members/"
        if store["link"]:
            link = "https://www.southcentralbank.com" + store["link"]

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
