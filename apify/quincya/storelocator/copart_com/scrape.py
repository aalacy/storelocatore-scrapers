from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    base_link = "https://www.copart.com/public/data/locations/retrieveLocationsList?continentCode=NORTH_AMERICA"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    store_data = session.get(base_link, headers=headers).json()["data"]["countries"]

    locator_domain = "copart.com"

    for country in store_data:
        states = store_data[country]["yardByStates"]
        for state_item in states:
            stores = state_item["yards"]

            for store in stores:
                location_name = store["yardName"]
                street_address = (
                    (store["yardAddress1"] + " " + store["yardAddress2"])
                    .replace("INSURANCE SELLERS ONLY", "")
                    .strip()
                )
                city = store["yardCity"]
                state = store["yardStateCode"]
                zip_code = store["yardZip"]
                country_code = (
                    store["yardCountryCode"].replace("USA", "US").replace("CAN", "CA")
                )
                if country_code == "US":
                    zip_code = zip_code.replace(" ", "-")
                store_number = store["yardNumber"]
                location_type = "<MISSING>"
                phone = store["yardPhoneAreaCode"] + store["yardPhoneNumber"]
                hours_of_operation = (
                    store["yardDays"].replace("through", "To")
                    + " "
                    + store["yardHours"]
                )
                latitude = store["yardLatitude"]
                longitude = store["yardLongitude"]
                if latitude == 0:
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
                link = "https://www.copart.com" + store["locationUrl"]

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
