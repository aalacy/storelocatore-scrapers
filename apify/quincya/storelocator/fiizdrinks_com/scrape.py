import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    base_link = "https://www.fiizdrinks.com/new-locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "https://www.fiizdrinks.com"

    response = session.get(base_link, headers=headers)
    base = BeautifulSoup(response.text, "lxml")

    items = base.find_all(id="af")

    for item in items:
        if "COMING SOON" in item.text.upper():
            continue
        location_name = item.h1.text.strip()
        try:
            raw_address = list(
                item.find(string="Directions").find_previous("p").stripped_strings
            )[1:]
        except:
            raw_address = list(
                item.find(string="Address").find_previous("p").stripped_strings
            )[1:]
        street_address = raw_address[0]
        city = raw_address[1].split(",")[0]
        state = raw_address[1].split(",")[1].split()[0].strip()
        zip_code = raw_address[1].split(",")[1].split()[1].strip()
        country_code = "CA"
        location_type = ""
        phone = item.a.text
        if not phone[2].isdigit():
            phone = ""

        try:
            hours_of_operation = (
                " ".join(list(item.table.stripped_strings))
                .replace(" Weather & Event Permitting", "")
                .strip()
            )
        except:
            hours_of_operation = ""
        store_number = ""
        try:
            map_str = item.find(string="Directions").find_previous()["href"]
            geo = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", map_str)[0].split(
                ","
            )
            latitude = geo[0]
            longitude = geo[1]
        except:
            latitude = ""
            longitude = ""
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


with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))) as writer:
    fetch_data(writer)
