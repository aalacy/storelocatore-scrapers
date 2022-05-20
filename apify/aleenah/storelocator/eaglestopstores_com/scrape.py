import usaddress
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from typing import Iterable

import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


website = "eaglestopstores_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

DOMAIN = "https://eaglestopstores.com/"
MISSING = SgRecord.MISSING


payload = "action=store_wpress_listener&method=display_map&page_number=1&lat=&lng=&category_id=&max_distance=&nb_display=100"
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
}

API_ENDPOINT_URL = "https://eaglestopstores.com/wp-admin/admin-ajax.php"


def fetch_records(http: SgRequests) -> Iterable[SgRecord]:
    loclist = http.post(API_ENDPOINT_URL, headers=headers, data=payload).json()[
        "locations"
    ]
    for loc in loclist:
        location_name = loc["name"]
        log.info(location_name)
        store_number = loc["id"]
        latitude = loc["lat"]
        longitude = loc["lng"]
        phone = loc["tel"]
        hours_of_operation = MISSING
        address = loc["address"]
        address = address.replace(",", " ")
        address = usaddress.parse(address)
        i = 0
        street_address = ""
        city = ""
        state = ""
        zip_postal = ""
        while i < len(address):
            temp = address[i]
            if (
                temp[1].find("Address") != -1
                or temp[1].find("Street") != -1
                or temp[1].find("Recipient") != -1
                or temp[1].find("Occupancy") != -1
                or temp[1].find("BuildingName") != -1
                or temp[1].find("USPSBoxType") != -1
                or temp[1].find("USPSBoxID") != -1
            ):
                street_address = street_address + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                zip_postal = zip_postal + " " + temp[0]
            i += 1
        country_code = "US"
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url="https://eaglestopstores.com/locations/",
            location_name=location_name,
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code=country_code,
            store_number=store_number,
            phone=phone.strip(),
            location_type=MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation.strip(),
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        with SgRequests(proxy_country="us") as http:
            for rec in fetch_records(http):
                writer.write_row(rec)
                count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
