import unicodedata
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "billabong_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://billabong.com/"
MISSING = SgRecord.MISSING


def strip_accents(text):
    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")
    return str(text)


def fetch_data():
    if True:
        url = "https://www.billabong.com/on/demandware.store/Sites-BB-US-Site/en_US/StoreLocator-StoreLookup?mapRadius=200000&filterBBStores=true&filterBBRetailers=true&latitude=37.75870132446288&longitude=-122.4811019897461"
        loclist = session.get(url, headers=headers).json()["stores"]
        page_url = "https://www.billabong.com/stores/"
        for loc in loclist:
            location_name = strip_accents(loc["name"])
            store_number = loc["ID"]
            log.info(location_name)
            phone = loc["phone"]
            street_address = strip_accents(loc["address"]).split("\n")[0]
            if "., 16" in street_address:
                street_address = MISSING
            city = strip_accents(loc["city"])
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
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
