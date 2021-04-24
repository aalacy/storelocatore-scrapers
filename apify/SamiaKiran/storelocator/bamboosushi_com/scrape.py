from sglogging import SgLogSetup
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()

DOMAIN = "https://bamboosushi.com/"
website = "bamboosushi_com"
log = SgLogSetup().get_logger(logger_name=website)
MISSING = "<MISSING>"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():

    url = "https://bamboosushi.com/restaurants"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    loclist = soup.find("div", {"class": "locations-listing"}).findAll(
        "a", {"class": "location-single"}
    )

    for idx, loc in enumerate(loclist):
        locator_domain = DOMAIN
        page_url = loc["href"]
        log.info(
            f"{idx} out of {len(loclist)} Stores][Pulling the data from: {page_url} "
        )

        # Response from page URL
        r = session.get(page_url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")

        # Address
        address = (
            soup.find("div", {"class": "location-addr"})
            .get_text(separator="|", strip=True)
            .split("|")
        )

        # Location Name
        location_name = " ".join(address[0].strip().split())
        location_name = location_name if location_name else MISSING
        log.info(f"[Location Name: {location_name}]")

        # Street Address
        street_address = address[1].strip()
        street_address = street_address if street_address else MISSING
        log.info(f"[Street Address: {street_address}]")

        # City
        address2 = address[2].split(",")
        city = address2[0].strip()
        city = city if city else MISSING
        log.info(f"[City: {city}]")

        # State
        address3 = address2[1].split()
        state = address3[0].strip()
        state = state if state else MISSING
        log.info(f"[State: {state}]")

        # Zip
        zip_postal = address3[1].strip()
        zip_postal = zip_postal if zip_postal else MISSING
        log.info(f"[Zip: {zip_postal}]")

        # Country Code
        country_code = "US"

        # Store Number
        store_number = loc["restaurant_id"].strip()
        store_number = store_number if store_number else MISSING
        log.info(f"[Store Number: {store_number}]")

        # Phone
        phone = (soup.find("div", {"class": "location-phone"}).text).strip()
        phone = phone if phone else MISSING

        # Location Type
        location_type = MISSING

        # Latitude
        latitude = MISSING

        # Longitude
        longitude = MISSING

        # Hours of operation
        hoo = (
            soup.find("div", {"class": "location-hours"})
            .get_text(separator="|", strip=True)
            .replace("|", " ")
            .strip("-")
        )
        hours_of_operation = hoo if hoo else MISSING
        log.info(f"[Hours of Operation: {hours_of_operation}]")

        # Raw Address
        raw_address = ", ".join(address[1:])
        raw_address = raw_address if raw_address else MISSING
        log.info(f"[Raw Address: {raw_address}]")

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
