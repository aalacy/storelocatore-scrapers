import re
import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://bohemian-studios.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    all_scripts = base.find_all("script")
    for script in all_scripts:
        if "mapLng" in str(script):
            script = str(script)
            break

    raw_address = list(base.find(class_="Footer-business-info").stripped_strings)
    locator_domain = "bohemian-studios.com"

    location_name = raw_address[0]
    street_address = raw_address[1]
    if street_address[-1:] == ",":
        street_address = street_address[:-1]
    city_line = raw_address[2].strip().split(",")
    city = city_line[0].strip()
    state = city_line[1].strip()
    zip_code = ""
    if "Fauntleroy" in street_address:
        zip_code = "98116"
    country_code = "US"
    store_number = "<MISSING>"
    location_type = "<MISSING>"
    phone = "<MISSING>"

    geo = re.findall(r'mapLat"\:[0-9]{2}\.[0-9]+,"mapLng":-[0-9]{2,3}\.[0-9]+', script)[
        0
    ]
    latitude = geo.split(",")[0].split(":")[1]
    longitude = geo.split(",")[1].split(":")[1]

    raw_hours = re.findall(r'"businessHours.+}]}}', script)[0]
    js = json.loads(raw_hours[16:])
    hours_of_operation = ""
    for day in js:
        hours_of_operation = (
            hours_of_operation + " " + day.title() + " " + js[day]["text"]
        ).strip()

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
