from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sglogging import sglog

MISSING = "<MISSING>"
website = "https://www.hawaiianbarbecue.com"
session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def requests_with_retry(url):
    return session.get(url, headers=headers).json()


def fetchData():
    # store_number is not available
    url = "https://www.hawaiianbarbecue.com/page-data/sq/d/1339288897.json"
    r = requests_with_retry(url)

    x = r["data"]["allPrismicLocation"]["nodes"]
    log.info(f"Total restaurants = {len(x)}")

    for i in x:
        data = i["data"]
        page_url = website + str(i["url"])
        location_name = data["title"]["text"]
        location_type = data["type"]
        street_address = data["street_address"]["text"]
        city = data["city"]["text"]
        state = data["state"]["text"]
        zip_postal = data["zip_code"]["text"]
        phone = data["phone_number"]["text"]

        try:
            latitude = data["coordinates"]["latitude"]
            longitude = data["coordinates"]["longitude"]
        except Exception as e:
            latitude, longitude = MISSING, MISSING
            log.info(f"Invalid Location {e}")
            pass

        store_number = i["uid"]
        country_code = data["country"]["text"]
        if country_code == "":
            country_code = "US"

        hours_of_operation = ""
        operations = []
        for day in days:
            value = data[f"{day.lower()}_hours"]["text"]
            if value == "":
                value = "closed"
            operations.append(f"{day}: {value}")
        hours_of_operation = ", ".join(operations)

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
            location_type=location_type,
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    log.info("Started")
    count = 0
    results = fetchData()
    with SgWriter() as writer:
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
