import json
import re

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from bs4 import BeautifulSoup

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.bncollege.com/campus-stores/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    script = (
        str(base.find(id="bnc-map-js-extra"))
        .split("bncLocationsByState = ")[1]
        .split("]};")[0]
        + "]}"
    )

    states = json.loads(script)
    locator_domain = "bncollege.com"

    for i in states:
        stores = states[i]
        for store in stores:
            location_name = store["title"]
            country_code = "US"
            raw_address = store["address"].replace(",", "\n").split("\n")
            city = raw_address[-2].strip()
            street_address = (
                (
                    store["address"][: store["address"].rfind(city)]
                    .replace("\n", " ")
                    .strip()
                )
                .replace("  ", " ")
                .replace("Ivy Tech Community College - Illinois Fall Creek Center", "")
                .strip()
            )
            if street_address[-1:] == ",":
                street_address = street_address[:-1].strip()

            if location_name == "Hanover College":
                street_address = "One Campus Dr"

            if location_name == "Hartwick College":
                street_address = "1 Hartwick Drive Dewar Hall, 3rd Flr"

            if location_name == "Cuesta College San Luis Obispo Campus":
                street_address = "-1"
                city = "San Luis Obispo"

            if "530 S. State Street" in city:
                street_address = "530 S. State Street"
                city = "Ann Arbor"

            if "1300 nevada state drive" in city:
                street_address = "1300 nevada state drive"
                city = "Henderson"

            if "1 Saxton Drive" in city:
                street_address = "1 Saxton Drive"
                city = "Alfred"

            if "Liverpool L69 3BX" in city:
                city = "Liverpool"
                zip_code = "L69 3BX"
                country_code = "UK"

            if "210 Cowan Blvd" in street_address:
                country_code = "CA"
                zip_code = "N1T 1V4"

            if "versity of St Francis Fort" in street_address:
                street_address = street_address.split("Fort")[0].strip()

            if street_address == "ollege Dr":
                street_address = "One College Drive"

            if street_address == "versity Dr":
                street_address = "One University Drive"

            if street_address == "versity Pl":
                street_address = "One University Place"

            if street_address == "ollege Ave":
                street_address = "College Ave"

            if street_address == "versity Cir":
                street_address = "University Cir"

            if not street_address:
                street_address = "<MISSING>"

            if re.search(r"\d", street_address):
                digit = str(re.search(r"\d", street_address))
                start = int(digit.split("(")[1].split(",")[0])
                street_address = street_address[start:]

            state = store["state_code"].upper()
            zip_code = store["address"][store["address"].rfind(state) + 2 :].strip()
            zip_code = zip_code.replace("240132222", "24013")
            if not zip_code.isdigit() and country_code == "US":
                zip_code = "<MISSING>"
            store_number = store["id"]
            location_type = ", ".join(store["types"])

            if not location_type:
                location_type = "<MISSING>"

            phone = store["phone"]
            hours_of_operation = "<INACCESSIBLE>"
            latitude = store["lat"]
            longitude = store["lng"]
            page_url = store["url"]

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
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )
            )


with SgWriter(
    SgRecordDeduper(
        SgRecordID(
            {
                SgRecord.Headers.STREET_ADDRESS,
                SgRecord.Headers.CITY,
                SgRecord.Headers.LOCATION_TYPE,
            }
        )
    )
) as writer:
    fetch_data(writer)
