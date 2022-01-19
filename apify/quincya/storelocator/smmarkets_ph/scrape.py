import re

from bs4 import BeautifulSoup

from sgpostal.sgpostal import parse_address_intl

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    base_link = "https://corp.smmarkets.ph/search-market-maps"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "https://smmarkets.ph/"

    searches = ["save", "sm"]

    for search in searches:

        payload = {
            "token": "a5771bce93e200c36f7cd9dfd0e5deaa1d9c35e6b967d4efe220a0f1a48c6212",
            "keyword": search,
            "max": "288",
        }
        response = session.post(base_link, headers=headers, data=payload)
        base = BeautifulSoup(response.text, "lxml")

        items = base.find_all(class_="lower-map-detail")
        for item in items:

            location_name = item.find(class_="map-title").text.strip()

            raw_address = item.find(class_="map-address").text.strip()
            addr = parse_address_intl(raw_address)
            try:
                street_address = addr.street_address_1 + " " + addr.street_address_2
            except:
                street_address = addr.street_address_1
            city = addr.city
            if not city or city == "City":
                city = raw_address.split(",")[-1].strip()
                street_address = ", ".join(raw_address.split(",")[:-1])
            if not street_address:
                street_address = city
                city = ""
            if city:
                city = city.replace(".", "")
            state = addr.state
            zip_code = addr.postcode
            country_code = "Philippines"
            store_number = ""
            location_type = ""
            phone = ""

            if "Store Hours" in item.find_all(class_="map-address")[-1].text:
                hours_of_operation = (
                    item.find_all(class_="map-address")[-1]
                    .text.split("Hours:")[1]
                    .strip()
                )
            else:
                hours_of_operation = ""

            try:
                geo = re.findall(
                    r"[0-9]{1,2}\.[0-9]+,[0-9]{2,3}\.[0-9]+", item.a["href"]
                )[0].split(",")
                latitude = geo[0]
                longitude = geo[1]
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url="https://smmarkets.ph/store-locator",
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


with SgWriter(
    SgRecordDeduper(
        SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS})
    )
) as writer:
    fetch_data(writer)
