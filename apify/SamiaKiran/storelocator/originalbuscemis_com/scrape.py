from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "originalbuscemis_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}
session = SgRequests()
DOMAIN = "https://originalbuscemis.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    latlist = [
        "44.3148443,-85.60236429999999",
        "42.565576,-83.127351",
        "41.565576,-85.127351",
        "48.3056044,-82.1229766",
        "11.696118,-110.4181358",
    ]
    url = "https://originalbuscemis.com/wp-admin/admin-ajax.php"
    for i in range(0, len(latlist)):
        latnow = latlist[i].split(",")[0]
        longnow = latlist[i].split(",")[1]
        mydata = {
            "nonce": "58789e415c",
            "apikey": "71da911620ac133b0d303507b926ef6a",
            "action": "csl_ajax_search",
            "lat": latnow,
            "lng": longnow,
            "address": "",
        }
        loclist = session.post(url, data=mydata, headers=headers).json()
        loclist = loclist["response"]
        for loc in loclist:
            location_name = loc["name"]
            log.info(location_name)
            country_code = "US"
            street_address = loc["address"]
            city = loc["city"]
            state = loc["state"]
            zip_postal = loc["zip"]
            phone = loc["phone"]
            store_number = loc["id"]
            latitude = loc["lat"]
            longitude = loc["lng"]
            if "," in city:
                city = city.split(",")
                zip_postal = state
                state = city[1]
                city = city[0]
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name.strip(),
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
                hours_of_operation=MISSING,
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
