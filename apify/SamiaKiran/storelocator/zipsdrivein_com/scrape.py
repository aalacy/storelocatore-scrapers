import html
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


session = SgRequests()
website = "zipsdrivein_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


DOMAIN = "https://zipsdrivein.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.zipsdrivein.com/wp-json/wpgmza/v1/features"
        loclist = session.get(url, headers=headers).json()["markers"]
        for loc in loclist:
            raw_address = loc["address"].replace("USA", "")
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING
            phone = loc["description"]
            soup = BeautifulSoup(phone, "html.parser")
            temp = soup.get_text(separator="|", strip=True).split("|")
            phone = temp[-1]
            if "Hours:" in phone:
                phone = temp[-2]
            if "ID" in phone:
                phone = MISSING
            latitude = loc["lat"]
            longitude = loc["lng"]
            location_name = html.unescape(
                loc["title"].split(")")[1].replace(phone, "").split(" - ")[0]
            )
            log.info(location_name)
            country_code = "US"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url="https://www.zipsdrivein.com/locations/",
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
