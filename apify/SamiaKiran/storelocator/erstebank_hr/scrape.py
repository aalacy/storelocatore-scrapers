import unicodedata
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "erstebank_hr"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.erstebank.hr"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        loc_url = "https://www.erstebank.hr/en/branches-and-atms"
        daylist = {
            "0": "Mon",
            "1": "Tue",
            "2": "Wed",
            "3": "Thu",
            "4": "Fri",
            "5": "Sat",
            "6": "Sun",
        }
        url = "https://local.erstebank.hr/rproxy/webdocapi/f/branches"
        loclist = session.get(url, headers=headers).json()
        for loc in loclist:
            location_name = loc["name"]
            log.info(location_name)
            phone = loc["phone"]
            street_address = strip_accents(loc["address"])
            city = strip_accents(loc["city"])
            state = MISSING
            zip_postal = loc["zipcode"]
            country_code = loc["country"]
            latitude = loc["latitude"].replace(",", ".")
            longitude = loc["longitude"].replace(",", ".")
            store_number = loc["branch_id"]
            hour_list = loc["working_hours"][0]["days"]
            hours_of_operation = ""
            for idx, day in enumerate(hour_list):
                try:
                    weekday = daylist[str(idx)]
                    time = day["intervals"][0]
                    time = time["from"] + "-" + time["to"]
                except:
                    continue
                hours_of_operation = hours_of_operation + " " + weekday + " " + time
            hours_of_operation = (
                hours_of_operation.replace("ne radi-ne radi", "ne radi")
                + " Sun ne radi"
            )
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=loc_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )


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
