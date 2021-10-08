from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sglogging import SgLogSetup
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_coordinate_list

logger = SgLogSetup().get_logger("lesliespool_com")
session = SgRequests()


def fetch_data(sgw: SgWriter):
    headers = {
        "authority": "lesliespool.com",
        "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
        "accept": "application/json, text/javascript, */*; q=0.01",
        "x-requested-with": "XMLHttpRequest",
        "sec-ch-ua-mobile": "?0",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    }

    base_url = "https://www.lesliespool.com"
    coords = static_coordinate_list(radius=200, country_code=SearchableCountries.USA)
    for lat, lng in coords:
        logger.info(f"pulling stores for lat:{lat} long:{lng}")
        r = session.get(
            "https://lesliespool.com/on/demandware.store/Sites-lpm_site-Site/en_US/Stores-FindStores?showMap=false&radius=1000&referrer=dropdown&countryCode=US&lat={}&long={}".format(
                lat, lng
            ),
            headers=headers,
        ).json()

        try:
            stores = r["stores"]
        except:
            continue
        for dt in stores:
            page_url = ""
            if dt["contentAssetId"]:
                page_url = "https://lesliespool.com/" + dt["contentAssetId"] + ".html"
            location_name = dt["name"].lower()
            street_address = ""
            street_address1 = ""
            if dt["address2"]:
                street_address1 = dt["address2"].lower()
            street_address = dt["address1"].lower() + " " + street_address1
            city = dt["city"].lower()
            zipp = dt["postalCode"]
            state = dt["stateCode"]
            if dt["latitude"] == 0:
                latitude = ""
                longitude = ""
            else:
                latitude = dt["latitude"]
                longitude = dt["longitude"]

            hours_of_operation = (
                dt["storeHours"]
                .replace("*", " ")
                .replace("Hours not scheduled for this gro", "")
            )
            phone = dt["phone"]
            store_number = dt["ID"]
            location_type = ""

            sgw.write_row(
                SgRecord(
                    locator_domain=base_url,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zipp,
                    country_code="US",
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
