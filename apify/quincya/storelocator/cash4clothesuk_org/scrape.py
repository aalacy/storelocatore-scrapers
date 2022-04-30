from bs4 import BeautifulSoup

from sgpostal.sgpostal import parse_address_intl

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    base_link = "https://www.cash4clothesuk.org/#x_our-centres"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    all_scripts = base.find_all("script")
    for script in all_scripts:
        if "uk_areas" in str(script):
            script = str(script).split("[\n")[1].split("\n];")[0].strip()
            break

    items = script.split("[")[1:]

    locator_domain = "https://www.cash4clothesuk.org"

    for item in items:
        store = BeautifulSoup(item, "lxml")
        raw_data = list(store.div.stripped_strings)
        location_name = "Cash For Clothes"
        phone = ""
        for i, row in enumerate(raw_data):
            if "call" in row:
                phone = row.split("number ")[1].split(" ")[0].strip()
            if "monday" in row.lower():
                hours_of_operation = (
                    " ".join(raw_data[i:])
                    .split("(")[0]
                    .split("*")[0]
                    .replace("Opening Hours", "")
                    .title()
                    .split("Closed")[0]
                    .strip()
                )
                if "holiday" in hours_of_operation.lower()[-20:]:
                    hours_of_operation = hours_of_operation + " Closed"
                break

        raw_address = ""
        for i, row in enumerate(raw_data):
            if (
                "(" not in row
                and "Clothes" not in row
                and "day" not in row
                and "**" not in row
                and "Opening" not in row
            ):
                raw_address = raw_address + " " + row
            if len(row.strip()) == 7 and " " == row.strip()[3]:
                zip_code = row.strip()
                raw_address = raw_address.replace(zip_code, "").strip()
                break

        addr = parse_address_intl(raw_address)
        try:
            street_address = addr.street_address_1 + " " + addr.street_address_2
        except:
            street_address = addr.street_address_1

        if len(street_address) < 10:
            street_address = raw_address
        city = addr.city
        state = addr.state
        if "Glasgow" in street_address:
            city = "Glasgow"
            street_address = street_address[: street_address.rfind(city)].strip()
        if "Gillingham" in street_address:
            city = "Gillingham"
            street_address = street_address[: street_address.rfind(city)].strip()

        country_code = "GB"
        store_number = ""
        location_type = "<MISSING>"
        latitude = store.p.text.split(",")[-4]
        longitude = store.p.text.split(",")[-3]
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
                raw_address=raw_address,
            )
        )


with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))) as writer:
    fetch_data(writer)
