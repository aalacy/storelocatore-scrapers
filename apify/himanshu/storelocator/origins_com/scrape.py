from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sgpostal import sgpostal as parser
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import sglog

website = "origins.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    with SgRequests() as session:
        data = "JSONRPC=%5B%7B%22method%22%3A%22locator.doorsandevents%22%2C%22id%22%3A5%2C%22params%22%3A%5B%7B%22fields%22%3A%22DOOR_ID%2C+DOORNAME%2C+EVENT_NAME%2C+EVENT_START_DATE%2C+EVENT_END_DATE%2C+EVENT_IMAGE%2C+EVENT_FEATURES%2C+EVENT_TIMES%2C+SERVICES%2C+STORE_HOURS%2C+ADDRESS%2C+ADDRESS2%2C+STATE_OR_PROVINCE%2C+CITY%2C+REGION%2C+COUNTRY%2C+ZIP_OR_POSTAL%2C+PHONE1%2C+STORE_TYPE%2C+LONGITUDE%2C+LATITUDE%2C+SUB_HEADING%22%2C%22radius%22%3A%2210000000000%22%2C%22country%22%3A%22%22%2C%22region_id%22%3A%220%22%2C%22latitude%22%3A33.755711%2C%22longitude%22%3A-84.3883717%2C%22uom%22%3A%22mile%22%7D%5D%7D%5D"
        r = session.post(
            "https://www.origins.com/rpc/jsonrpc.tmpl?dbgmethod=locator.doorsandevents",
            headers=headers,
            data=data,
        )
        data = r.json()[0]["result"]["value"]["results"]
        for key in data:
            store_data = data[key]
            line = (store_data["ADDRESS"] + " " + store_data["ADDRESS2"]).strip()
            adr = parser.parse_address_intl(line)
            street_address = (
                f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
                    "None", ""
                ).strip()
                or "<MISSING>"
            )
            locator_domain = "https://www.origins.com"
            location_name = store_data["DOORNAME"].strip()
            city = store_data["CITY"] if store_data["CITY"] != "" else "<MISSING>"
            state = (
                store_data["STATE_OR_PROVINCE"]
                if store_data["STATE_OR_PROVINCE"] != ""
                else "<MISSING>"
            )
            zip = (
                store_data["ZIP_OR_POSTAL"]
                if store_data["ZIP_OR_POSTAL"] != ""
                else "<MISSING>"
            )
            if store_data["COUNTRY"] == "United States":
                country_code = "US"
            elif store_data["COUNTRY"] == "Canada":
                country_code = "CA"
            else:
                continue
            if store_data["ZIP_OR_POSTAL"] == "":
                continue

            store_number = key
            phone = (
                store_data["PHONE1"]
                if store_data["PHONE1"] != "" and store_data["PHONE1"] != "TBD"
                else "<MISSING>"
            )
            location_type = "origins"
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
                else "<MISSING>"
            )
            page_url = "<MISSING>"
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
