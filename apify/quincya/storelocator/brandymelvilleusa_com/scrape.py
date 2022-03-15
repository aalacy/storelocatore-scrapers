import json
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://locations.brandymelville.com/"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "brandymelville.com"

    all_scripts = base.find_all("script")
    for script in all_scripts:
        if "locations = {" in str(script):
            script = str(script)
            break

    js = script.split('data":')[1].split("};\n\n")[0].strip()
    items = json.loads(js)

    for i in items:
        country_code = i
        states = items[i]

        for state in states:
            stores = states[state]

            for store in stores:
                street_address = (
                    store[1]
                    .split(", Nashville")[0]
                    .replace(", Beijing", "")
                    .replace(", Hong Kong", "")
                    .strip()
                )
                city = store[0]
                state = state.replace("Washington", "WA")
                location_name = "Brandy Melville - " + city
                phone = store[2]
                hours_of_operation = store[4]

                map_link = store[3]
                if "@" in map_link:
                    latitude = map_link.split("@")[1].split(",")[0]
                    longitude = map_link.split("@")[1].split(",")[1].split(",")[0]
                else:
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"

                store_number = "<MISSING>"
                location_type = "<MISSING>"
                if city == "London":
                    state = "<MISSING>"
                zip_code = "<MISSING>"
                if not phone:
                    phone = "<MISSING>"
                if "coming" in phone:
                    phone = "<MISSING>"

                if country_code == "United States":
                    try:
                        zip_code = re.findall(r"[(\d)]{5}", store[1][-10:])[0]
                    except:
                        pass

                if country_code in ["United States", "Canada"]:
                    if re.search(r"\d", street_address):
                        digit = str(re.search(r"\d", street_address))
                        start = int(digit.split("(")[1].split(",")[0])
                        street_address = street_address[start:]

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
