from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "accessstorage.ca"

    base_link = "https://datavault-api.storagevaultcanada.com/api/location/nearest_locations/?lat=43.7615936&lng=-79.35694010000002&distance=5000&lang=en&originlat=43.7615936&originlng=-79.35694010000002"

    stores = session.get(base_link, headers=headers).json()

    for store_data in stores:
        link = store_data["url"]
        if "accessstorage.ca" not in link:
            continue
        location_name = store_data["title"]
        raw_address = store_data["address"].split(",")
        street_address = ",".join(raw_address[:-1])
        city_line = (
            raw_address[-1].replace("S6J1M3", "S6J 1M3").replace("L4W1C2", "L4W 1C2")
        )
        city = " ".join(city_line.split()[:-3])
        state = city_line.split()[-3]
        zip_code = " ".join(city_line.split()[-2:])
        phone = store_data["phone"]
        country_code = "CA"
        location_type = ""
        store_number = store_data["lcode"]
        latitude = store_data["latlng"]["lat"]
        longitude = store_data["latlng"]["lng"]
        hours = store_data["hour"]
        hours_of_operation = ""
        for day in hours:
            hours_of_operation = (
                hours_of_operation + " " + day + " " + hours[day]
            ).strip()

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
