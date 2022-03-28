from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "hoopershealth_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://hoopershealth.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://hoopershealth.com/index.php/contact/location/"
        r = session.get(url, headers=headers)
        loclist = r.text.split(
            '<div class="shortcode-wrapper shortcode-title clearfix">'
        )[1:]
        for loc in loclist:
            longitude = loc.split('data-map-lng="')[1].split('"')[0]
            latitude = loc.split('data-map-lat="')[1].split('"')[0]
            temp = loc.split("address:")[1].split("fax")[0]
            temp = (
                BeautifulSoup(temp, "html.parser")
                .get_text(separator="|", strip=True)
                .split("|")
            )
            loc = BeautifulSoup(loc, "html.parser")
            location_name = loc.find("h3").text
            log.info(location_name)
            raw_address = temp[0].strip()
            phone = temp[1].replace("tel:", "")
            hours_of_operation = (
                loc.findAll("div", {"class": "hb-box-cont-body"})[-1]
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Store Hours", "")
            )
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING

            country_code = "CA"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
                raw_address=raw_address,
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
