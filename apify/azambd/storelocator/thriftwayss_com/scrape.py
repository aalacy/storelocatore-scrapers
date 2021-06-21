import time

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sglogging import sglog

session = SgRequests()

website = "thriftwayss.com"

log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def requests_with_retry(url):
    return session.get(url, headers=headers).json()


def fetchData():
    l = "https://www.thriftwayss.com/wp-json/wpgmza/v1/features/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMoxR0gEJFGeUFni6FAPFomOBAsmlxSX5uW6ZqTkpELFapVoABU0Wug"
    j = requests_with_retry(l)

    data = j["markers"]
    log.info(f"Total Locations: {len(data)}")

    for d in data:
        page_url = d["link"]
        location_name = d["title"]
        address = d["address"]
        address_parts = address.split(" ")
        zip_postal = address_parts[len(address_parts) - 1]
        state = address_parts[len(address_parts) - 2]
        city = address_parts[len(address_parts) - 3].replace(",", "")
        street_address = (
            address.replace(city, "")
            .replace(state, "")
            .replace(zip_postal, "")
            .replace(",", "")
        )
        country_code = "US"
        phone = d["description"].split("<br>")[0].replace("Store Phone :", "").strip()
        store_number = d["id"]
        latitude = d["lat"]
        longitude = d["lng"]
        hours_of_operation = ""
        raw_address = address

        yield SgRecord(
            locator_domain=website,
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
            raw_address=raw_address,
        )


def scrape():
    log.info("Started")
    count = 0
    start = time.time()
    result = fetchData()
    with SgWriter() as writer:
        for rec in result:
            writer.write_row(rec)
            count = count + 1

    end = time.time()
    log.info(f"Total Rows Added= {count}")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
