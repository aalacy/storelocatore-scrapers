import json

from bs4 import BeautifulSoup

from geopy.geocoders import Nominatim

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgpostal.sgpostal import parse_address_usa

from sgrequests import SgRequests

geolocator = Nominatim(user_agent="geoapiExercises")


def fetch_data(sgw: SgWriter):

    base_link = "https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/6973/stores.js?callback=SMcallback2"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    stores = json.loads(base.text.split('stores":')[1].split("})")[0])

    for store in stores:
        locator_domain = "abcstores.com"
        location_name = store["name"]

        addr = parse_address_usa(store["address"])
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address = street_address + " " + addr.street_address_2
        city = addr.city
        try:
            state = addr.state.split(",")[0].strip().upper()
        except:
            state = addr.state
        zip_code = addr.postcode
        country_code = addr.country

        try:
            if "Northern" in country_code:
                continue
        except:
            pass

        if "Bayview Phase" in street_address:
            street_address = store["address"]

        latitude = store["latitude"]
        longitude = store["longitude"]

        location = geolocator.reverse(str(latitude) + "," + str(longitude))
        address = parse_address_usa(location.address)
        add_split = location.address.split(",")
        if not state:
            state = address.state
        if not city:
            city = address.city
        if not country_code:
            country_code = address.country
        if not zip_code:
            zip_code = address.postcode

        if not state:
            state = add_split[-3].strip()
        if not city:
            city = add_split[-4].replace("County", "").strip()
        if not zip_code:
            zip_code = add_split[-2].strip()

        store_number = location_name.split("#")[-1].strip().split("-")[0].strip()
        if not store_number[0].isdigit():
            store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = store["phone"]

        hours_of_operation = store["custom_field_1"]
        if not hours_of_operation:
            hours_of_operation = "<MISSING>"

        link = "https://abcstores.com/store-mapper/"

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=link,
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
