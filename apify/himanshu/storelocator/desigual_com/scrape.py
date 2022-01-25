from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "desigual_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://desigual.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        country_list = ["en_US", "en_CA"]
        for country in country_list:
            country_url = (
                "https://www.desigual.com/"
                + country
                + "/shops/?showMap=true&horizontalView=true&isForm=true"
            )
            r = session.get(country_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            loclist = soup.find("ul", {"id": "collapseExample"}).findAll("li")
            for loc in loclist:
                page_url = loc.find("a")["href"]
                log.info(page_url)
                r = session.get(page_url, headers=headers)
                temp = (
                    r.text.split('initial-stores="')[1]
                    .split('">')[0]
                    .replace("&quot;", " ")
                )
                store_number = temp.split("id :")[1].split(",")[0]
                location_name = temp.split("name :")[1].split(",")[0]
                street_address = temp.split("address :")[1].split(", city :")[0]
                city = temp.split(", city :")[1].split(",")[0]
                state = temp.split("regionSapId :")[1].split(",")[0]
                zip_postal = temp.split("postalCode :")[1].split(",")[0]
                country_code = temp.split("countryCode :")[1].split(",")[0]
                latitude = temp.split("latitude :")[1].split(",")[0]
                longitude = temp.split("longitude :")[1].split(",")[0]
                phone = temp.split("phone : ")[1].split(",")[0]
                mon = "Mon " + temp.split("Monday , value :")[1].split(",")[0]
                tue = "Tue " + temp.split("Tuesday , value :")[1].split(",")[0]
                wed = "Wed " + temp.split("Wednesday , value :")[1].split(",")[0]
                thu = "Thu " + temp.split("Thursday , value :")[1].split(",")[0]
                fri = "Fri " + temp.split("Friday , value :")[1].split(",")[0]
                sat = "Sat " + temp.split("Saturday , value :")[1].split(",")[0]
                sun = "Sun " + temp.split("Sunday , value :")[1].split(",")[0]
                hours_of_operation = (
                    mon
                    + ", "
                    + tue
                    + ", "
                    + wed
                    + ", "
                    + thu
                    + ", "
                    + fri
                    + ", "
                    + sat
                    + ", "
                    + sun
                )
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
