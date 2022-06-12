import json
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "motoguzzi_com"
log = SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}
DOMAIN = "https://motoguzzi.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://www.motoguzzi.com/us_EN/moto-guzzi/us/legacy-map/?f=all"
        r = session.get(url, headers=headers)
        loclist = r.text.split(" PointsJson: ")[1].split("}}]},")[0]
        loclist = loclist + "}}]}"
        loclist = loclist.replace("'", "\\'")
        loclist = json.loads(loclist)["features"]
        for loc in loclist:
            address = loc["properties"]
            location_name = address["companyname"].replace("\\", "")
            street_address = address["address"]
            city = address["city"]
            state = address["prov"]
            zip_postal = address["cap"]
            country_code = "US"
            country_code = address["country"]
            phone = address["phone1"]
            latitude = address["lat"]
            longitude = address["lng"]
            page_url = (
                "https://www.motoguzzi.com/us_EN/dealer-locator/"
                + address["seouri"]
                + "/"
            )
            log.info(page_url)
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
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
                hours_of_operation=MISSING,
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
