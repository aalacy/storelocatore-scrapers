import json
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "jhcc_com"
log = SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}
DOMAIN = "https://jhcc.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://jhcc.com/body-shop-locations/"
        r = session.get(url, headers=headers)
        loclist = r.text.split("var locationsApi = ")[1].split("}}};")[0]
        loclist = loclist + "}}}"
        loclist = json.loads(loclist)
        for loc in loclist:
            loc = loclist[loc]
            address = loc["location"]
            location_name = loc["name"]
            street_address = address["address"]
            city = address["city"]
            state = address["state"]
            coords = address["geo"]
            zip_postal = address["zip"]
            phone = loc["phone"]
            country_code = "US"
            latitude = coords["latitude"]
            longitude = coords["longitude"]
            hours_of_operation = loc["businessHours"]
            hours_of_operation = (
                "Opens: "
                + hours_of_operation["from"]
                + " - "
                + "Closes: "
                + hours_of_operation["until"]
            )
            log.info(location_name)
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=MISSING,
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
