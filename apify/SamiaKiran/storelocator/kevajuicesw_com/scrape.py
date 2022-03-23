import json
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "kevajuicesw_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.kevajuicesw.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        location_url = "https://www.kevajuicesw.com/locations"
        r = session.get(location_url, headers=headers)
        user_id = r.text.split("user_id: '")[1].split("'")[0]
        site_id = r.text.split("site_id: '")[1].split("'")[0]
        url = (
            "https://cdn5.editmysite.com/app/store/api/v18/editor/users/"
            + user_id
            + "/sites/"
            + site_id
            + "/store-locations?page=1&per_page=100&include=address&lang=en&valid=1"
        )
        loclist = session.get(url, headers=headers).json()["data"]
        for loc in loclist:
            location_name = loc["display_name"]
            if "Keva Juice Southwest, LLC  # 10" in location_name:
                continue
            store_number = loc["id"]
            temp = loc["address"]["data"]
            phone = temp["phone"]
            street_address = temp["street"]
            log.info(street_address)
            city = temp["city"]
            state = temp["region_code"]
            zip_postal = temp["postal_code"]
            country_code = temp["country_code"]
            latitude = temp["latitude"]
            longitude = temp["longitude"]
            hours_of_operation = ""
            try:
                hour_list = json.loads(loc["square_business_hours"])["periods"]
                for hour in hour_list:
                    hours_of_operation = (
                        hours_of_operation
                        + " "
                        + hour["day_of_week"]
                        + " "
                        + hour["start_local_time"]
                        + "-"
                        + hour["end_local_time"]
                    )
            except:
                hours_of_operation = str(loc["pickup_hours"])
                hours_of_operation = (
                    hours_of_operation.replace("': [{'open': '", " ")
                    .replace("', 'close': '", "-")
                    .replace("'}], '", " ")
                    .replace("': [], '", " Closed ")
                    .replace("{'", "")
                    .replace("'}]}", "")
                )

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=location_url,
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
                hours_of_operation=hours_of_operation,
            )


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
