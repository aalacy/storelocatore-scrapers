import time
import json
from lxml import html

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sglogging import sglog

# F
MISSING = "<MISSING>"
DOMAIN = "acehardware.com"
website = "https://www.acehardware.com"
session = SgRequests().requests_retry_session()
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
}

days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


def request_with_retries(url):
    response = session.get(url, headers=headers)
    return html.fromstring(response.text, "lxml")


def fetchData():
    dataUrl = "https://www.acehardware.com/store-directory"
    r = request_with_retries(dataUrl)
    rj = r.xpath('//script[@id="data-mz-preload-storeDirectory"]/text()')
    jsonData = json.loads(rj[0])
    log.info(f"Total Locations: {len(jsonData)}")
    for loc in jsonData:
        store_number = loc["code"] or MISSING
        location_name = loc["name"] or MISSING
        street_address = loc["address"]["address1"] or MISSING
        city = loc["address"]["cityOrTown"] or MISSING
        state = loc["address"]["stateOrProvince"] or MISSING
        zip_postal = loc["address"]["postalOrZipCode"] or MISSING
        country_code = loc["address"]["countryCode"] or MISSING
        phone = loc["formattedPhoneNumber"] or MISSING
        hours = loc["regularHours"]
        h = []
        for day in days:
            value = hours[f"{day.lower()}"]["label"]
            if value == "0000 - 0000":
                value = "closed"
            h.append(f"{day}:{value}")
            hours_of_operation = "; ".join(h) or MISSING

        page_url = "https://www.acehardware.com/store-details/" + str(store_number)
        log.info(f"Location Name: {location_name} & {page_url}")
        dpBody = request_with_retries(page_url)
        try:
            dpr = dpBody.xpath('//script[@id="data-mz-preload-store"]/text()')
            jsonDp = json.loads(dpr[0])
            latitude = jsonDp["Latitude"]
            longitude = jsonDp["Longitude"]
        except:
            latitude = MISSING
            longitude = MISSING

        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            phone=phone,
            location_type="",
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    log.info("Started")
    count = 0
    start = time.time()

    with SgWriter() as writer:
        result = fetchData()
        for rec in result:
            writer.write_row(rec)
            count = count + 1

    end = time.time()
    log.info(f"Total Rows Added= {count}")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
