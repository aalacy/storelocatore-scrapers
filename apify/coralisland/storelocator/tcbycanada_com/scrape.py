from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


session = SgRequests()
website = "tcbycanada_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()


headers = {
    "User-Agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1",
}

DOMAIN = "https://tcbycanada.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://tcbycanada.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=fr&t=1567446471949"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("item")
        for loc in loclist:
            location_name = loc.find("location").text
            raw_address = loc.find("address").text
            if "6140 Cote St Luc  Montreal" in raw_address:
                raw_address = "6142 Cote Saint Luc Rd  Montreal,  QC H3X 2G9"
            log.info(raw_address)
            store_number = loc.find("sortord").text
            latitude = loc.find("latitude").text
            longitude = loc.find("longitude").text
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url="https://tcbycanada.com/trouvez-une-tcby/",
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code="CA",
                store_number=store_number,
                phone=MISSING,
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=MISSING,
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
