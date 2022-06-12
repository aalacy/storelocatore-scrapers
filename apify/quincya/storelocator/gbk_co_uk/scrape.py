import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://gbk.co.uk/find-your-gbk"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "https://gbk.co.uk"

    js = (
        str(base)
        .replace("&quot;", '"')
        .split('restaurants="')[1]
        .split('" recaptcha')[0]
    )
    stores = json.loads(js)

    for store_data in stores:
        link = store_data["permalink"]
        location_name = store_data["title"]
        location_type = "Booking, Delvery"
        try:
            street_address = store_data["address_lines"][0]["address_line"]
        except:
            street_address = ""
        city = store_data["city"]
        if city in street_address.strip()[-len(city) :]:
            street_address = " ".join(street_address.split(",")[:-1])
        state = store_data["county_region"]
        if not state:
            state = "<MISSING>"
        zip_code = store_data["zip_postal_code"]
        country_code = "GB"
        store_number = store_data["restaurant_id"]
        if not store_number:
            store_number = "<MISSING>"
        phone = store_data["telephone_display"]
        if not phone:
            phone = "<MISSING>"
        latitude = store_data["latitude"]
        longitude = store_data["longitude"]

        hours_of_operation = ""
        raw_hours = store_data["opening_hours"]
        for hours in raw_hours:
            day = hours["day"]
            if hours["restaurant_closed"]:
                times = "Closed"
            else:
                opens = hours["opening_time"]
                closes = hours["closing_time"]
                times = opens + "-" + closes
            if opens != "" and closes != "":
                clean_hours = day + " " + times
                hours_of_operation = (hours_of_operation + " " + clean_hours).strip()
        if not hours_of_operation:
            hours_of_operation = "<MISSING>"
        if not street_address:
            location_type = "Delivery"

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
