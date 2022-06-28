import json
import re
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "eurekarestaurantgroup_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://eurekarestaurantgroup.com"
MISSING = SgRecord.MISSING


def fetch_data():
    soup = BeautifulSoup(
        session.get("https://eurekarestaurantgroup.com/locations").text, "lxml"
    )
    for url in soup.find_all(class_="location-links"):
        page_url = DOMAIN + url.a["href"]
        log.info(page_url)
        store_resp = session.get(page_url).text
        location_soup = BeautifulSoup(store_resp, "lxml")
        js = location_soup.find(id="__NEXT_DATA__").contents[0]
        store = json.loads(js)["props"]["pageProps"]["data"]["data"]

        location_name = store["name"]
        if " soon" in location_name.lower():
            continue

        street_address = store["address_line_1"]
        if store["address_line_2"]:
            street_address = street_address + " " + store["address_line_2"]
        if store["address_line_3"]:
            street_address = (
                street_address
                + " "
                + store["address_line_3"].replace("Cupertino", "").strip()
            )

        if re.search(r"\d", street_address):
            digit = str(re.search(r"\d", street_address))
            start = int(digit.split("(")[1].split(",")[0])
            street_address = street_address[start:]

        street_address = (
            street_address.replace("The Willows", "").replace("Main Street", "").strip()
        )

        city = store["city"]
        state = store["state"]
        zip_postal = store["zip"]
        country_code = "US"
        store_number = ""

        try:
            phone = store["phone"].strip()
        except:
            continue

        hours_of_operation = ""
        try:
            raw_hours = store["hours"]
            for row in raw_hours:
                day = row["day"]
                hours = row["store_hours"]
                hours_of_operation = (
                    hours_of_operation + " " + day + " " + hours
                ).strip()
        except:
            hours_of_operation = ""

        latitude = store["latitude"]
        longitude = store["longitude"]

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
            phone=phone,
            location_type=MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation.strip(),
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
