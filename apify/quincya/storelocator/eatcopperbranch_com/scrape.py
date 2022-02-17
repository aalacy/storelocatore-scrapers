from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    base_link = "https://eatcopperbranch.com/locations/"

    locator_domain = "https://eatcopperbranch.com"

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = list(base.find(class_="et_pb_text_inner").stripped_strings)

    for item in items:
        if "," not in item or "& MARKHAM" in item.upper():
            location_name = item.replace("\xa0", "")
            continue
        raw_address = (
            item.replace("\xa0", "")
            .replace(", ON ", ", ON, ")
            .replace(" QC", ", QC")
            .replace(" ON", ", ON")
            .replace(" TN ", " TN, ")
            .replace(" AB ", " AB, ")
            .replace(" BC ", " BC, ")
            .replace(" ME ", " ME, ")
            .replace(" NS ", " NS, ")
            .replace(",,", ",")
        )
        if "/" in raw_address:
            phone = raw_address.split("/")[-1].strip()
            raw_address = raw_address.split("/")[0].strip().split(",")
        else:
            raw_address = raw_address.strip().split(",")
            phone = ""

        street_address = ", ".join(raw_address[:-3])
        if not street_address:
            street_address = raw_address[0]
        street_address = street_address.split(",")[0].strip()
        city = raw_address[-3].strip()
        state = raw_address[-2].strip()
        zip_code = raw_address[-1].strip()
        if len(zip_code) == 5:
            country_code = "US"
        else:
            country_code = "CA"

        if street_address == city:
            city = state
            state = ""

        if city == "Toronto":
            state = "ON"

        if state == "C":
            state = "QC"

        store_number = "<MISSING>"
        location_type = "<MISSING>"
        latitude = ""
        longitude = ""
        hours_of_operation = ""

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
