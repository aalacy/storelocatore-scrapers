from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "mena_sunglasshut_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://mena.sunglasshut.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://mena.sunglasshut.com/api/content/render/false/limit/9999/type/json/query/+contentType:SghStoreLocator%20+languageId:11%20+deleted:false%20+working:true/orderby/modDate%20desc"
        loclist = session.get(url, headers=headers).json()["contentlets"]
        for loc in loclist:
            try:
                street_address = loc["address"] + " " + loc["address2"]
            except:
                street_address = loc["address"]
            city = loc["city"]
            state = loc["state"]
            zip_postal = loc["zip"]
            country_code = loc["innerCountry"]
            phone = loc["phone"]
            location_name = loc["name"]
            page_url = (
                "https://mena.sunglasshut.com/en/store-locator/" + loc["exampleUrl"]
            )
            log.info(page_url)
            hours_of_operation = (
                "mon "
                + loc["monday"]
                + " "
                + "tues "
                + loc["tuesday"]
                + " "
                + "wed "
                + loc["wednesday"]
                + " "
                + "thu "
                + loc["thursday"]
                + " "
                + "fri "
                + loc["friday"]
                + " "
                + "sat "
                + loc["saturday"]
                + " "
                + "sun "
                + loc["sunday"]
            )
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=hours_of_operation.strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
