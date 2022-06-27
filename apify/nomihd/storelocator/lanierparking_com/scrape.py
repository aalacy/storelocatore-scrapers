# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

website = "lanierparking.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "manageparking.citizensparking.com",
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://manageparking.citizensparking.com/FindParking/MainFindParkingResult",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():

    api_url = "https://manageparking.citizensparking.com/FindParking/FindParkers?searchPlaceLat=34.0522342&searchPlaceLng=-118.2436849&latNorthEast=70.91647331027256&lngNorthEast=-65.069856775&latSouthWest=-28.420842456987156&lngSouthWest=-171.417513025&_=1655267697899"
    with SgRequests() as session:
        api_res = session.get(api_url, headers=headers)

        try:
            stores_sel = lxml.html.fromstring(api_res.text)
            store_list = stores_sel.xpath('//input[@class="json-parker"]')
            for store in store_list:
                page_url = "https://manageparking.citizensparking.com/FindParking/MainFindParkingResult"
                store_json = json.loads(
                    "".join(store.xpath("@value"))
                    .strip()
                    .replace("&quot;", '"')
                    .strip()
                )
                locator_domain = website

                street_address = store_json["Address"].split("(")[0].strip()
                if street_address:
                    if "," == street_address[-1]:
                        street_address = "".join(street_address[:-1]).strip()

                city = store_json["City"]
                state = store_json["State"]
                zip = store_json["ZIP"]

                if street_address:
                    if street_address == "6200 HOLLYWOOD BLVD HOLLYWOOD , CA":
                        street_address = "6200 HOLLYWOOD BLVD"
                        city = "HOLLYWOOD"
                        state = "CA"

                country_code = "US"

                location_name = store_json["Name"]
                log.info(location_name)
                phone = store_json["Phone"]
                if phone:
                    if (
                        not phone.replace("(", "")
                        .replace(")", "")
                        .replace("-", "")
                        .strip()
                        .replace(" ", "")
                        .strip()
                        .isdigit()
                    ):
                        phone = "<MISSING>"

                store_number = store_json["ParkerId"]

                location_type = store_json["SrcParkingIconThumbnail"]
                if location_type:
                    location_type = (
                        location_type.replace("../Images/Images/", "")
                        .strip()
                        .replace("-thumbnail.png", "")
                        .strip()
                    )

                hours_of_operation = "<MISSING>"

                latitude, longitude = (
                    store_json["Lat"],
                    store_json["Lng"],
                )
                yield SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )
        except:
            pass


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
