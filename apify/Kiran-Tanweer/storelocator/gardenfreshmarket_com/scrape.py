from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "gardenfreshmarket_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.gardenfreshmarket.com"
MISSING = SgRecord.MISSING


def fetch_data():
    url = "https://www.gardenfreshmarket.com/store-locator"
    stores_req = session.get(url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    blocks = soup.findAll("div", {"class": "col sqs-col-6 span-6"})
    for block in blocks:
        info = block.find("div", {"class": "sqs-block-content"}).findAll("p")
        location_name = info[0].text
        log.info(location_name)
        address = str(info[1])
        address = address.split('pre-wrap;">')[1]
        address = address.rstrip("</p>")
        address = address.replace(",", "<br/>")
        address = address.split("<br/>")
        street_address = address[0].strip()
        city = address[1].strip()
        state = address[2].strip()
        phone = address[3].strip()
        info2 = block.find("div", {"class": "sqs-block map-block sqs-block-map"})[
            "data-block-json"
        ]
        info2 = str(info2)
        latitude = info2.split('"mapLat":')[1].split(",")[0]
        longitude = info2.split('"mapLng":')[1].split(",")[0]
        zip_postal = (
            info2.split('"addressLine2":"')[1].split('","')[0].split(",")[-1].strip()
        )
        country_code = "US"
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
