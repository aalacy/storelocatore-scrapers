from re import L
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl
from sglogging import sglog

DOMAIN = "origins.com"
API_URL = "https://www.origins.com/rpc/jsonrpc.tmpl?dbgmethod=locator.doorsandevents"
LOCATION_URL = "https://www.origins.com/store-locator"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
}
MISSING = SgRecord.MISSING
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def fetch_data():
    with SgRequests() as session:
        data = "JSONRPC=%5B%7B%22method%22%3A%22locator.doorsandevents%22%2C%22id%22%3A2%2C%22params%22%3A%5B%7B%22fields%22%3A%22DOOR_ID%2C+DOORNAME%2C+EVENT_NAME%2C+EVENT_START_DATE%2C+EVENT_END_DATE%2C+EVENT_IMAGE%2C+EVENT_FEATURES%2C+EVENT_TIMES%2C+SERVICES%2C+STORE_HOURS%2C+ADDRESS%2C+ADDRESS2%2C+STATE_OR_PROVINCE%2C+CITY%2C+REGION%2C+COUNTRY%2C+ZIP_OR_POSTAL%2C+PHONE1%2C+STORE_TYPE%2C+LONGITUDE%2C+LATITUDE%2C+SUB_HEADING%22%2C%22radius%22%3A2210000000000%2C%22country%22%3A%22%22%2C%22region_id%22%3A%220%22%2C%22latitude%22%3A35.1660032%2C%22longitude%22%3A-80.7934798%2C%22uom%22%3A%22mile%22%2C%22_TOKEN%22%3A%2293eeb395884edc7eee174473653a348ca154321a%2Cef96f3840cb406ddb115fbeec9cde0b0537540ec%2C1648802446%22%7D%5D%7D%5D"
        r = session.get(API_URL + "&" + data, headers=HEADERS)
        data = r.json()[0]["result"]["value"]["results"]
        for key in data:
            store_data = data[key]
            line = (store_data["ADDRESS"] + " " + store_data["ADDRESS2"]).strip()
            adr = parse_address_intl(line)
            street_address = (
                f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
                    "None", ""
                ).strip()
                or MISSING
            )
            location_name = store_data["DOORNAME"].strip()
            city = store_data["CITY"]
            state = store_data["STATE_OR_PROVINCE"]
            zip = store_data["ZIP_OR_POSTAL"]
            if store_data["COUNTRY"] == "United States":
                country_code = "US"
            elif store_data["COUNTRY"] == "Canada":
                country_code = "CA"
            else:
                country_code = store_data["COUNTRY"]
            store_number = key
            phone = (
                store_data["PHONE1"]
                if store_data["PHONE1"] != "" and store_data["PHONE1"] != "TBD"
                else MISSING
            )
            if "Origins" in store_data["DOORNAME"]:
                location_type = "Origins"
            else:
                location_type = MISSING
            latitude = store_data["LATITUDE"]
            longitude = store_data["LONGITUDE"]
            hours_of_operation = (
                " ".join(
                    list(
                        BeautifulSoup(
                            store_data["STORE_HOURS"], "lxml"
                        ).stripped_strings
                    )
                ).replace("\xa0", " ")
                if store_data["STORE_HOURS"] != ""
                else MISSING
            )
            log.info("Append {} => {}".format(location_name, street_address))
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=LOCATION_URL,
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


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
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
