from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    locator_domain = "https://ewingirrigation.com/"

    store_link = "https://ewingirrigation.com/graphql?query=query+getLocationList%28%24pageSize%3AInt%29%7BMpStoreLocatorLocations%28pageSize%3A%24pageSize%29%7Bitems%7Blocation_id+location_code+name+street+state_province+postal_code+images+description+phone_one+email+fax+latitude+longitude+city+country+services+open_today+today_hours_data%7Bfrom_time+to_time%7Dlocation_filters+location_time_data%7Bday+from_time+to_time%7D%7Dtotal_count+total_filters%7Bcode+label%7D%7D%7D&operationName=getLocationList&variables=%7B%22pageSize%22%3A300%7D"

    stores = session.get(store_link, headers=headers).json()["data"][
        "MpStoreLocatorLocations"
    ]["items"]

    for store in stores:
        location_name = store["name"]
        street_address = store["street"]
        city = store["city"]
        state = store["state_province"]
        zip_code = store["postal_code"]
        country_code = "US"
        store_number = store["location_id"]
        location_type = ""
        phone = store["phone_one"]
        latitude = store["latitude"]
        longitude = store["longitude"]

        hours_of_operation = ""
        raw_hours = store["location_time_data"]
        for hours in raw_hours:
            day = hours["day"]
            opens = hours["from_time"]
            closes = hours["to_time"]
            if opens != "Closed":
                clean_hours = day + " " + opens + "-" + closes
            else:
                clean_hours = day + " " + opens
            hours_of_operation = (hours_of_operation + " " + clean_hours).strip()

        link = (
            "https://ewingirrigation.com/locations/locationDetails/details?id="
            + str(store_number)
        )

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
