from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json
import re
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("canadacomputers_com")
MISSING = "<MISSING>"
DOMAIN = "https://www.canadacomputers.com"
LOCATION_URL = "https://www.canadacomputers.com/location.php"
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
}

session = SgRequests()


def fetch_data():
    r = session.get(LOCATION_URL, headers=headers)
    d = re.findall(r"var markers(.*)", r.text)[0]
    d = d.replace(";", "").strip().lstrip("=")
    d = d.strip()
    data_json = json.loads(d)
    for data in data_json:
        location_name = data["name"]
        locator_domain = DOMAIN
        id_ = data["id"]
        page_url = f"https://www.canadacomputers.com/location_details.php?loc={id_}"
        address = data["address"]
        a1 = address.split(",")
        street_address = a1[0] or MISSING
        city = a1[-3] or MISSING
        state = data["province"]
        zip_postal = a1[-2].strip().split(" ")
        zip_postal = zip_postal[-2] + " " + zip_postal[-1]
        country_code = a1[-1]
        if "Canada" in country_code:
            country_code = "CA"
        else:
            if country_code:
                country_code = country_code
            else:
                country_code = MISSING
        store_number = MISSING
        phone = data["phone"] or MISSING
        location_type = data["type"]
        latitude = data["lat"]
        longitude = data["lng"]
        hours_of_operation = data["hours"]
        if hours_of_operation:
            hours_of_operation = hours_of_operation.replace("<br/>", "; ")
        else:
            hours_of_operation = MISSING

        raw_address = data["address"]

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
    logger.info(" Scraping Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
