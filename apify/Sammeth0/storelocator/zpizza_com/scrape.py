from sgrequests import SgRequests
from sgselenium import SgSelenium
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

session = SgRequests()
DOMAIN = "zpizza.com"
BASE_URL = "https://www.zpizza.com/"
LOCATION_URL = "https://www.zpizza.com/locations"
headers = {
    "Accept": "*/*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
}

MISSING = "<MISSING>"


log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def fetch_data():
    script = """
        return fetch('/graphql', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
            body: JSON.stringify({ "operationName": "restaurantPageContent", "variables": { "draftMode": false, "restaurantId": 6265, "url": "/locations" }, "extensions": { "operationId": "PopmenuClient/8ab8c2ade9f3deb1346d180fa26c7c78" } })
        })
        .then(r => r.json())
    """
    driver = SgSelenium().chrome()
    driver.get("https://www.zpizza.com/locations")
    info = driver.execute_script(script)
    driver.quit()
    store_info = info["data"]["restaurant"]["pageContent"]["sections"][0]["locations"]
    for row in store_info:
        page_url = "https://www.zpizza.com/" + row["slug"]
        if "moreno-valley-tap-room" in row["slug"]:
            page_url = page_url = "https://www.zpizza.com/moreno-valley-ca"
        location_name = row["name"]
        if page_url.find("bend-tap-room") > -1:
            page_url = page_url.split("-")[0]
        raw_address = row["fullAddress"]
        store_number = row["id"]
        street_address = row["streetAddress"]
        state = row["state"]
        city = row["city"]
        zip_postal = row["postalCode"]
        country_code = row["country"]
        latitude = row["lat"]
        longitude = row["lng"]
        hourlist = row["schemaHours"]
        phone = row["displayPhone"]
        location_type = "zpizza"
        hours_of_operation = ""
        hourd = []
        hourd.append("none")
        try:
            for hr in hourlist:
                dt = hr.split(" ", 1)[0]
                if dt in hourd:
                    pass
                else:
                    hourd.append(dt)
                    day = (int)(hr.split("-")[1].split(":")[0])
                    if day > 12:
                        day = day - 12
                    hours_of_operation = (
                        hours_of_operation
                        + hr.split("-")[0]
                        + " am "
                        + " - "
                        + str(day)
                        + ":00 PM"
                    )
                    hours_of_operation = hours_of_operation + " "
            hours_of_operation = (
                hours_of_operation.replace("Su", "Sunday")
                .replace("Mo", "Monday")
                .replace("Tu", "Tuesday")
                .replace("We", "Wednesday")
                .replace("Th", "Thursday")
                .replace("Fr", "Friday")
                .replace("Sa", "Saturday")
            )
        except:
            hours_of_operation = MISSING
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
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
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.RAW_ADDRESS,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
