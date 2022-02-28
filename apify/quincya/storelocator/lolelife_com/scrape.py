from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    base_link = "https://www.lolelife.com/store-locator"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    req = session.get(base_link, headers=headers)
    base = str(BeautifulSoup(req.text, "lxml"))

    locator_domain = "lolelife.com"

    items = (
        base.split("store-locator")[-1]
        .split('png",')[1]
        .split(',"Search')[0]
        .split(",")
    )

    for item in items:
        link = "https://www.lolelife.com/store-locator/" + item.replace('"', "")
        api_link = (
            "https://www.lolelife.com/maps.googleapis/maps/api/place/details/json?key=AIzaSyA11_18TL_SMVLQj5cWoS9neD0iVxP2NMQ&place_id="
            + item.replace('"', "")
        )

        store = session.get(api_link, headers=headers).json()["result"]
        raw_address = BeautifulSoup(store["adr_address"], "lxml")

        location_name = store["name"]
        street_address = raw_address.find(class_="street-address").text
        city = raw_address.find(class_="locality").text
        state = raw_address.find(class_="region").text
        zip_code = raw_address.find(class_="postal-code").text
        country_code = raw_address.find(class_="country-name").text
        store_number = ""
        location_type = "<MISSING>"
        try:
            phone = store["international_phone_number"]
        except:
            phone = ""
        try:
            hours_of_operation = " ".join(store["opening_hours"]["weekday_text"])
        except:
            hours_of_operation = ""

        latitude = store["geometry"]["location"]["lat"]
        longitude = store["geometry"]["location"]["lng"]

        if "Beaver Creek" in city:
            location_name = "Lolë Beaver Creek"

        if "3720 N" in location_name:
            location_name = "Lolë Canyon"

        if "3001 N" in location_name:
            location_name = "Lolë Lake Tahoe"

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
