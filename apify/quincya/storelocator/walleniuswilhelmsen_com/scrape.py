import re
from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgpostal.sgpostal import parse_address_intl

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    base_link = (
        "https://www.walleniuswilhelmsen.com/where-you-find-us/all-locations-list"
    )

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "walleniuswilhelmsen.com"

    items = base.find_all(class_="tabcontent facts-content")

    for item in items:
        location_type = item["id"].split("0")[-1].replace("Poi", "").upper().strip()
        names = item.find_all(class_="mb-2")
        addresses = item.find_all(class_="address")

        for i, name in enumerate(names):
            location_name = name.text.strip()
            raw_address = " ".join(list(addresses[i].li.stripped_strings))
            raw_address = (re.sub(" +", " ", raw_address)).strip()
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address = street_address + " " + addr.street_address_2
            city = addr.city
            state = addr.state
            zip_code = addr.postcode
            country_code = addr.country

            if city and "China" in city:
                city = city.replace("China", "").strip()
                country_code = "China"

            if city and "Mexico" in city:
                city = ""
                country_code = "Mexico"

            if not country_code and "Mexico" in street_address:
                country_code = "Mexico"
                street_address = street_address.replace(country_code, "").strip()

            if street_address:
                if street_address.replace("-", "").isdigit() or len(street_address) < 8:
                    street_address = list(addresses[i].li.stripped_strings)[0]
            try:
                if country_code in street_address[-50:]:
                    street_address = street_address.replace(country_code, "").strip()
            except:
                pass

            if city == "Sao":
                city = "Sao Paulo"
                state = "<MISSING>"

            if zip_code == "6A3":
                zip_code = "V3M 6A3"

            if "28F LOTTE World Tower" in raw_address:
                street_address = "28F LOTTE World Tower 300 Olympic-Ro Songpa-gu 0555"
                city = "Seoul"
                state = "<MISSING>"
                country_code = "Korea, Republic of"

            store_number = "<MISSING>"
            try:
                phone = addresses[i].a.text.strip()
            except:
                phone = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours_of_operation = "<MISSING>"

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


with SgWriter(
    SgRecordDeduper(
        SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_TYPE})
    )
) as writer:
    fetch_data(writer)
