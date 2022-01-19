from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "keyfoodstores_keyfood_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://keyfoodstores.keyfood.com/store/"
MISSING = SgRecord.MISSING


def fetch_data():
    page = 0
    while True:
        data = session.get(
            "https://www.keyfood.com/store/keyFood/en/store-locator?q=11756&page="
            + str(page)
            + "&radius=5000000000&all=true",
            headers=headers,
        ).json()["data"]
        for store_data in data:
            store_number = store_data["name"]
            location_name = store_data["displayName"]
            try:
                street = store_data["line1"] + " " + store_data["line2"]
            except:
                store_data["line1"]
            zip_code = store_data["postalCode"]
            if "10305" in street:
                street.replace("10305", "").strip()
                zip_code = "10305"
            street_address = street
            city = store_data["town"]
            state = store_data["state"]
            zip_postal = zip_code
            country_code = "US"
            phone = store_data["phone"] if store_data["phone"] else "<MISSING>"
            page_url = store_data["siteUrl"] + store_data["url"].split("?")[0]
            latitude = store_data["latitude"]
            longitude = store_data["longitude"]
            req = session.get(page_url, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
            try:
                location_type = base.find(class_="banner__component simple-banner").img[
                    "title"
                ]
            except:
                location_type = MISSING
            try:
                hours = ""
                for hour in store_data["openings"]:
                    hours = hours + " " + hour + " " + store_data["openings"][hour]
            except:
                hours = "<MISSING>"
            hours_of_operation = hours.strip() if hours else "<MISSING>"
            log.info(page_url)
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
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
        if len(data) < 250:
            break
        page = page + 1


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
