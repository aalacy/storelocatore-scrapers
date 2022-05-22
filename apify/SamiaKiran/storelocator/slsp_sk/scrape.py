from datetime import date
import unicodedata
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "slsp_sk"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.slsp.sk"
MISSING = SgRecord.MISSING


def strip_accents(text):
    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")
    return str(text)


def fetch_data():
    if True:
        daylist = {
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday",
        }
        url = "https://www.slsp.sk/bin/erstegroup/gemesgapi/locations/gem_site_location_locations-sk-slsp?types=pobocka&items=1000&page=0"
        loclist = session.get(url, headers=headers).json()
        for loc in loclist:
            store_number = loc["ouId"]
            address = loc["address"]
            street_address = strip_accents(address["street"])
            city = strip_accents(address["city"])
            try:
                state = strip_accents(address["region"])
            except:
                state = MISSING
            zip_postal = address["zipCode"]
            country_code = address["countryCode"]
            latitude = loc["location"]["latitude"]
            longitude = loc["location"]["longitude"]
            page_url = (
                "https://www.slsp.sk/sk/ludia/kontakty/pobocka/"
                + zip_postal.replace(" ", "-")
                + "-"
                + city.lower().replace(".", "").replace(" ", "-")
                + "/"
                + street_address.lower().replace(" ", "-")
                + "/"
                + store_number
            )
            log.info(page_url)
            location_name = strip_accents(loc["description"])
            phone = MISSING
            hour_list = loc["openingHoursWithDates"]
            hours_of_operation = ""
            for hour in hour_list:
                day = hour["date"].split(".")
                day = date(int(day[-1]), int(day[-2]), int(day[-3])).weekday()
                day = daylist[day]
                time = hour["periods"]
                if time:
                    time1 = time[0]["open"] + "-" + time[0]["close"]
                    try:
                        time2 = time[1]["open"] + "-" + time[1]["close"]
                    except:
                        time2 = ""
                    hours_of_operation = (
                        hours_of_operation + " " + day + " " + time1 + ", " + time2
                    )
            hours_of_operation = hours_of_operation.strip()
            hours_of_operation = " Monday" + hours_of_operation.split("Monday", 2)[1]
            if "Saturday" not in hours_of_operation:
                hours_of_operation = hours_of_operation + "Saturday Closed"
            if "Sunday" not in hours_of_operation:
                hours_of_operation = hours_of_operation + " Sunday Closed"
            hours_of_operation = hours_of_operation.strip().strip(",")
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
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
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
