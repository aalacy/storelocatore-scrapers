import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "wasabi_uk_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://wasabi.uk.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://api.wasabi.uk.com/wp-json/wp/v2/location?per_page=100"
        loclist = session.get(url, headers=headers).json()
        for loc in loclist:
            location_name = loc["yoast_title"]
            if "(Delivery Only)" in location_name:
                location_type = "Delivery Only"
            else:
                location_type = MISSING
            page_url = (
                location_name.replace("(Delivery Only)", "")
                .split("-")[0]
                .strip()
                .lower()
                .replace(" ", "-")
            )
            page_url = "https://www.wasabi.uk.com/location/" + page_url
            log.info(page_url)
            store_number = str(loc["id"])
            loc = loc["acf"]
            latitude = str(loc["position"]["lat"])
            longitude = str(loc["position"]["lng"])
            try:
                temp = (
                    str(loc["flexible_content"])
                    .split("'phone_number':")[1]
                    .split("]}]")[0]
                    .replace("'", '"')
                )
                temp = json.loads('{"phone_number":' + temp + "]}")
            except:
                temp = (
                    str(loc["flexible_content"])
                    .split("'phone_number':")[1]
                    .split("}]}")[0]
                    .replace("'", '"')
                )
                temp = json.loads('{"phone_number":' + temp + "}]}")
            phone = temp["phone_number"]
            address = temp["address"]
            address = BeautifulSoup(address, "html.parser")
            raw_address = address.get_text(separator="|", strip=True).replace("|", " ")
            hour_list = temp["opening_hours_schema"]
            hours_of_operation = ""
            for hour in hour_list:
                hours_of_operation = (
                    hours_of_operation
                    + " "
                    + hour["week_day"]
                    + " "
                    + hour["opening_hours"]
                )
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING
            country_code = "UK"
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
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
                raw_address=raw_address,
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
