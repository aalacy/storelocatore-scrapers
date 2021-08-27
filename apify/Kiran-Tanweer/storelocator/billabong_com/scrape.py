from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "billabong_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
}

DOMAIN = "https://billabong.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://www.billabong.com/on/demandware.store/Sites-BB-US-Site/en_US/StoreLocator-StoreLookup?mapRadius=200000&filterBBStores=true&filterBBRetailers=true&latitude=37.75870132446288&longitude=-122.4811019897461"
        loclist = session.get(url, headers=headers).json()["stores"]
        page_url = "https://www.billabong.com/stores/"
        for loc in loclist:
            location_name = loc["name"]
            store_number = loc["ID"]
            log.info(location_name)
            phone = loc["phone"]
            street_address = loc["address"]
            city = loc["city"]
            zip_postal = loc["postalCode"]
            country_code = loc["country"]
            latitude = loc["latitude"]
            longitude = loc["longitude"]
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=MISSING,
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=store_number,
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
