from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


session = SgRequests(proxy_country="bd")
website = "louispion_fr"
log = sglog.SgLogSetup().get_logger(logger_name=website)

DOMAIN = "https://louispion.fr/"
MISSING = SgRecord.MISSING


url = "https://boutiques.louispion.fr/controller/map/html/controller/components/region/0/departement/0/code_insee_ville/0/page/1/perpage/1000000/zoom/1200000/distance/50000/maxitems/1000000"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Referer": "https://boutiques.louispion.fr/",
    "Cookie": "PHPSESSID=9s71ls2tta7iugnv0clfdr2b93;SERVERID110649=STO-PROD-GRA-APP2|YcA32|YcArJ;",
}


def fetch_data():
    if True:
        r = session.get(url, headers=headers)
        loclist = r.text.split("entries[")[2:-1]
        for loc in loclist:
            page_url = loc.split('url : "')[1].split('"')[0]
            log.info(page_url)
            location_name = loc.split('title : "')[1].split('"')[0]
            store_number = loc.split('store_code: "')[1].split('"')[0]
            phone = loc.split('telephone : "')[1].split('"')[0]
            street_address = loc.split('adresse : "')[1].split('"')[0]
            city = loc.split('ville : "')[1].split('"')[0]
            state = MISSING
            zip_postal = loc.split(' code_postal : "')[1].split('"')[0]
            country_code = "FR"
            latitude = loc.split('latitude : "')[1].split('"')[0]
            longitude = loc.split('longitude : "')[1].split('"')[0]
            hours_of_operation = "<INACCESSIBLE>"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
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
