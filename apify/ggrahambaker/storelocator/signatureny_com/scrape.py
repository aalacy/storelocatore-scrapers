from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def addy_extractor(src):
    arr = src.replace("\xa0", " ").split(",")
    city = arr[0]
    prov_zip = arr[1].strip().split(" ")
    state = prov_zip[0].strip()
    zip_code = prov_zip[1].strip()

    return city, state, zip_code


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    locator_domain = "https://www.signatureny.com/"
    ext = "contact/private-client-offices"

    req = session.get(locator_domain + ext, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    tables = base.find_all(class_="table")
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            address = list(cols[0].stripped_strings)
            if "phone" in str(address).lower():
                end_row = 2
                phone_number = address[-1].split(":")[1].strip()
            else:
                end_row = 1
                phone_number = ""
            street_address = " ".join(address[:-end_row])
            if "(" in street_address:
                street_address = (
                    (street_address.split("(")[0] + street_address.split(")")[1])
                    .replace(" at", "")
                    .replace("  ", " ")
                    .strip()
                )
            city, state, zip_code = addy_extractor(address[-end_row])
            hours = list(cols[2].stripped_strings)[0]
            country_code = "US"
            store_number = "<MISSING>"
            location_type = "<MISSING>"
            lat = "<MISSING>"
            longit = "<MISSING>"
            location_name = "<MISSING>"

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=locator_domain + ext,
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
