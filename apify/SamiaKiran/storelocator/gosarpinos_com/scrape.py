import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "gosarpinos_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.gosarpinos.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.gosarpinos.com/sitemap"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("ul", {"class": "sitemap__list"})[-1].findAll("li")
        for loc in loclist:
            page_url = loc.find("a")["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            try:
                temp = json.loads(r.text.split("var data =")[1].split("};")[0] + "}")
            except:
                continue
            store_number = temp["storeId"]
            address = temp["stores"][0]
            location_name = address["name"]
            latitude = address["latitude"]
            longitude = address["longitude"]
            street_address = address["address"].replace(",", "")
            city = address["city"]
            state = address["state"]
            zip_postal = address["postalCode"]
            if zip_postal.isalpha():
                zip_postal = MISSING
            phone = address["phone"]
            hour_list = temp["schedule"]
            hours_of_operation = ""
            for hour in hour_list:
                day = hour["day"]
                time = hour["workingHours"]
                hours_of_operation = hours_of_operation + " " + day + " " + time
            country_code = "US"
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
                phone=phone,
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
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
