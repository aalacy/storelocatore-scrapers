import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def addy_ext(addy):
    address = addy.split(",")
    city = address[0]
    state_zip = address[1].strip().split(" ")
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code


def fetch_data(sgw: SgWriter):
    locator_domain = "https://www.omnisourceusa.com/"
    ext = "locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(locator_domain + ext, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    addys = base.find_all(class_="mb-3")
    for i in addys:
        addy = list(i.stripped_strings)
        location_name = addy[0]

        street_address = addy[1].replace(",", "")

        if len(addy) == 6:
            street_address += " " + addy[2].replace(",", "")
            off = 1
        else:
            off = 0
        city, state, zip_code = addy_ext(addy[off + 2])

        phone_number = addy[-1].replace("Phone:", "").strip()
        if "-" not in phone_number:
            phone_number = ""

        js = (
            str(base)
            .split("omniLocations =")[1]
            .split(";")[0]
            .replace("'", '"')
            .strip()
        )
        coords = json.loads(js)
        for coord in coords:
            if coord["name"] == location_name:
                lat = coord["lat"]
                longit = coord["lng"]
                store_number = coord["id"]

        country_code = "US"
        page_url = locator_domain + ext
        hours = "<MISSING>"
        location_type = "<MISSING>"

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone_number,
                location_type=location_type,
                latitude=lat,
                longitude=longit,
                hours_of_operation=hours,
            )
        )


with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))) as writer:
    fetch_data(writer)
