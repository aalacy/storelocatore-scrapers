from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://www.sunoco.com/js/locations.json"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()

    found = []
    locator_domain = "sunoco.com"

    for store in stores:
        location_name = "SUNOCO #" + str(store["Store_ID"])
        if location_name in found:
            continue
        found.append(location_name)
        street_address = store["Street_Address"].replace("  ", " ")
        city = store["City"]
        if "24205" in city:
            street_address = city
            city = "Farmington Hills".upper()
        state = store["State"]
        zip_code = str(store["Postalcode"])
        if len(zip_code) < 5:
            zip_code = "0" + zip_code
        if len(zip_code) < 4:
            zip_code = "<MISSING>"
        country_code = "US"
        store_number = store["Store_ID"]
        location_type = "<MISSING>"
        phone = store["Phone"]
        if len(str(phone)) < 5:
            phone = "<MISSING>"
        hours_of_operation = (
            "Mon %s Tue %s Wed %s Thu %s Fri %s Sat %s Sun %s"
            % (
                store["MON_Hours"],
                store["TUE_Hours"],
                store["WED_Hours"],
                store["THU_Hours"],
                store["FRI_Hours"],
                store["SAT_Hours"],
                store["SUN_Hours"],
            )
        ).strip()

        latitude = store["Latitude"]
        longitude = store["Longitude"]

        if not latitude or latitude == "NULL":
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        if str(latitude)[1].isdigit():
            if latitude < 0 and longitude > 0:
                latitude, longitude = longitude, latitude

        link = "https://www.sunoco.com/find-a-station"

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
