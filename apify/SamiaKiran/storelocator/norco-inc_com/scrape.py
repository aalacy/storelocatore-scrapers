import json
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "norco-inc_com"
log = SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}
DOMAIN = "https://norco-inc.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://www.norco-inc.com/Locations"
        r = session.get(url, headers=headers)
        loclist = r.text.split("var data = '")[1].split("';")[0]
        loclist = json.loads(loclist)
        for loc in loclist:
            street_address = loc["address2"]
            city = loc["city"]
            state = loc["state"]
            zip_postal = loc["zip"]
            country_code = loc["country"]
            phone = loc["phone"]
            latitude = loc["latitude"]
            longitude = loc["longitude"]
            if len(latitude.split(".")[0]) > 2:
                temp = latitude
                latitude = longitude
                longitude = "-" + temp
            if latitude == "0":
                latitude = MISSING
                longitude = MISSING
            store_number = MISSING
            hours_of_operation = loc["workHour"]
            hours_of_operation = hours_of_operation if street_address else MISSING
            location_name = loc["branchName"].replace("*", "")
            log.info(location_name)
            if "MAIN OFFICE" in location_name:
                street_address = loc["address1"]
            page_url = "https://www.norco-inc.com/Locations"

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
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
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
