from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    base_url = "https://www.cartersoshkosh.ca/"
    location_url = "https://www.cartersoshkosh.ca/on/demandware.store/Sites-CartersCA-SFRA-Site/en_CA/Stores-GetNearestStores?postalCode=&countryCode=CA&distanceUnit=imperial&maxdistance=1000000&lat=47.5702401&lng=-52.69563350000001"
    r = session.get(location_url, headers=headers)
    json_data = r.json()
    for key, value in json_data["stores"].items():
        store_number = value["storeid"]
        location_name = "Carter's OshKosh" + " " + str(value["mallName"])
        street_address = value["address1"] + " " + value["address2"]
        city = value["city"]
        zipp = value["postalCode"].replace("  ", " ")
        country_code = value["countryCode"]
        phone = value["phone"]
        latitude = value["latitude"]
        longitude = value["longitude"]
        location_type = ""
        state = value["stateCode"]
        hours_of_operation = (
            " sun "
            + value["sundayHours"]
            + " mon "
            + value["mondayHours"]
            + " Tues "
            + value["tuesdayHours"]
            + " Wed "
            + value["wednesdayHours"]
            + " Thurs "
            + value["thursdayHours"]
            + " Fri "
            + value["fridayHours"]
            + " Sat "
            + value["saturdayHours"]
        ).strip()
        locator_domain = base_url
        link = "https://www.cartersoshkosh.ca/en_CA/find-a-store?id=carters"

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=link,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipp,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
