from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "parkandshop_co_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://parkandshop.co.uk/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.parkandshop.co.uk/parkandshop2019/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=ff55d7bded&load_all=1&layout=1"
        loclist = session.get(url, headers=headers).json()
        for loc in loclist:
            location_name = loc["title"]
            log.info(location_name)
            store_number = loc["id"]
            phone = loc["phone"]
            street_address = loc["street"]
            city = loc["city"]
            state = loc["state"]
            zip_postal = loc["postal_code"]
            country_code = loc["country"]
            latitude = loc["lat"]
            longitude = loc["lng"]
            if latitude == "0.0":
                latitude = MISSING
                longitude = MISSING
            hours_of_operation = (
                str(loc["open_hours"])
                .replace('":["', " ")
                .replace('"],"', " ")
                .replace('{"', "")
                .replace('"]}', "")
            )
            if (
                'mon":"1","tue":"1","wed":"1","thu":"1","fri":"1","sat":"1","sun":"1"}'
                in hours_of_operation
            ):
                hours_of_operation = "Everyday: 24 Hours"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url="https://www.parkandshop.co.uk/store-locator/",
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
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
