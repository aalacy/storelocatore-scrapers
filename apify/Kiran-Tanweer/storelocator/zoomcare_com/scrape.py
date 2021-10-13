from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
import json

session = SgRequests()
website = "zoomcare_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.zoomcare.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://api-prod.zoomcare.com/v1/schedule/clinics"
        url = "https://api-prod.zoomcare.com/v1/schedule/clinics"
        stores_req = session.get(url, headers=headers)
        stores_req = json.loads(stores_req.text)
        for loc in stores_req:
            street = loc["address"]["line1"]
            street2 = loc["address"]["line2"]
            if street2 is not None:
                street = street + " " + street2
            else:
                street = street.strip()
            city = loc["address"]["city"]
            state = loc["address"]["state"]
            pcode = loc["address"]["postalCode"]
            storeid = loc["clinicId"]
            title = loc["name"]
            lat = loc["address"]["latitude"]
            lng = loc["address"]["longitude"]
            hours = loc["clinicHoursText"]
            hours = hours.replace("| ", ",")
            if hours.strip() == "":
                hoo = loc["clinicHours"]
                for hr in hoo:
                    day = hr["dayOfWeek"]
                    if day == 1:
                        day = "Monday"
                    elif day == 2:
                        day = "Tuesday"
                    elif day == 3:
                        day = "Wednesday"
                    elif day == 4:
                        day = "Thursday"
                    elif day == 5:
                        day = "Friday"
                    elif day == 6:
                        day = "Saturday"
                    else:
                        day = "Sunday"
                    start_time = str(hr["openHour"]) + ":" + str(hr["openMinute"]) + "0"
                    end_time = str(hr["closeHour"]) + ":" + str(hr["closeMinute"]) + "0"
                    hours = hours + " " + day + " " + start_time + " " + end_time
            if pcode is None:
                pcode = "<MISSING>"

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url="https://www.zoomcare.com/locations",
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode,
                country_code="US",
                store_number=storeid.strip(),
                phone=MISSING,
                location_type=MISSING,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours.strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LATITUDE, SgRecord.Headers.LONGITUDE},
                fail_on_empty_id=True,
            )
            .with_truncate(SgRecord.Headers.LATITUDE, 3)
            .with_truncate(SgRecord.Headers.LONGITUDE, 3)
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
