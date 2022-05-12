from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "picklemans_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.picklemans.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://parkerskitchen.com/wp-content/themes/parkers/get-locations.php?origAddress=8120+US-280%2C+Ellabell%2C+GA+31308%2C+USA"
        loclist = session.get(url, headers=headers).json()
        for loc in loclist:
            page_url = loc["web"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            temp = r.text.split('<div id="locations-text">')[1].split("</div>")[0]
            phone = temp.split("Phone:")[1].split("</p>")[0]
            hours_of_operation = (
                BeautifulSoup(temp, "html.parser")
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Limited Menu", "")
                .replace("*", "")
                .replace("Order Now", "")
                .replace("(Pay at Pump)", "")
                .replace("24 Hours Fuel Available 24/7", "")
                .replace("Fuel Available 24/7", "")
                .replace("Visit Website", "")
            )
            try:
                hours_of_operation = hours_of_operation.split("Kitchen Hours:")[1]
            except:
                hours_of_operation = hours_of_operation.split("Business Hours:")[1]
            hours_of_operation = hours_of_operation.replace(
                "Limited Menu Order Now", ""
            )
            store_number = loc["id"]
            location_name = loc["name"]
            try:
                street_address = loc["address"] + " " + loc["address2"]
            except:
                street_address = loc["address"]
            city = loc["city"]
            state = loc["state"]
            zip_postal = loc["postal"]
            country_code = "US"
            latitude = loc["lat"]
            longitude = loc["lng"]
            if "None" in hours_of_operation:
                hours_of_operation = MISSING
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
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
