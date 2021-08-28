import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    base_link = "https://order.pizzapaisanos.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    req = session.get(base_link, headers=headers)

    base = BeautifulSoup(req.text, "lxml")
    items = base.find_all(class_="StoreHeader")

    for item in items:
        locator_domain = "pizzapaisanos.com"
        location_name = item.find(class_="lblStoreName").text
        raw_address = list(item.find(id="StoreAddress").stripped_strings)
        street_address = raw_address[0].split("*")[0].strip()
        raw_line = raw_address[1]
        city = raw_line[: raw_line.rfind(",")].strip()
        state = raw_line[raw_line.rfind(",") + 1 : raw_line.rfind(" ")].strip()
        zip_code = raw_line[raw_line.rfind(" ") + 1 :].strip()
        country_code = "US"
        store_number = "<MISSING>"
        phone = item.find(id="StoreInfo").text.strip()
        location_type = "<MISSING>"
        hours = item.find_all(class_="HoursCenter")
        days = item.find_all(class_="HoursLeft")
        hours_of_operation = ""
        for i, row in enumerate(days):
            day = row.text.replace("Hours", "").strip()
            hour = hours[i].text.strip()
            hours_of_operation = hours_of_operation + " " + day + " " + hour
        hours_of_operation = hours_of_operation.replace("Pick Up\r\n", "")
        hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()

        latitude = "<MISSING>"
        longitude = "<MISSING>"

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=base_link,
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
