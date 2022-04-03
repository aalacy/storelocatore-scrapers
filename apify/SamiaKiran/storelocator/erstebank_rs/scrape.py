import unicodedata
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "erstebank_rs"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.erstebank.rs"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        loc_url = "https://www.erstebank.rs/sr/alati/bankomati-i-filijale/lista-filijale-bankomati"
        url = "https://moduli.erstebank.rs//aspx/filijale/branches.aspx"
        loclist = session.get(url, headers=headers).json()
        for loc in loclist:
            location_name = strip_accents(loc["branch_name"])
            log.info(location_name)
            store_number = loc["Id"]
            phone = loc["phone"]
            street_address = strip_accents(loc["address"])
            city = strip_accents(loc["city"])
            state = strip_accents(loc["country"])
            zip_postal = loc["zipcode"]
            country_code = "RS"
            latitude = loc["latitude"]
            longitude = loc["longitude"]
            mon = "Mon " + loc["opening_mon_to"] + "-" + loc["opening_mon_from"]
            tue = "Tue " + loc["opening_tue_to"] + "-" + loc["opening_tue_from"]
            wed = "Wed " + loc["opening_wed_to"] + "-" + loc["opening_wed_from"]
            thu = "Thu " + loc["opening_thu_to"] + "-" + loc["opening_thu_from"]
            fri = "Fri " + loc["opening_fri_to"] + "-" + loc["opening_fri_from"]
            sat = "Sat " + loc["opening_sat_to"] + "-" + loc["opening_sat_from"]
            sat = sat.replace("ne radi-ne radi", "ne radi")
            hours_of_operation = (
                mon + " " + tue + " " + wed + " " + thu + " " + fri + " " + sat
            )
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=loc_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=store_number,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
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
