from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "neworleanspizza_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://neworleanspizza.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://locations.neworleanspizza.com/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        api_token = soup.findAll("script")[-1]["src"]
        api_token = "https://locations.neworleanspizza.com/" + api_token
        r = session.get(api_token, headers=headers)
        api_token = r.text.split('"API_TOKEN","')[1].split('"')[0]
        url = (
            "https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token="
            + api_token
            + "&center=43.77166,-79.27583&coordinates=42.509130411498774,-76.93299552734257,45.0080893774996,-81.61866447265534&multi_account=false&page=1&pageSize=30"
        )
        loclist = session.get(url, headers=headers).json()
        for loc in loclist:
            page_url = "https://locations.neworleanspizza.com/" + loc["llp_url"]
            log.info(page_url)
            loc = loc["store_info"]
            location_type = MISSING
            if "temp closed" in loc["status"]:
                location_type = "Temporarily Closed"
                hours_of_operation = MISSING
            else:
                hours_of_operation = loc["store_hours"]
                if "7," not in hours_of_operation:
                    hours_of_operation = hours_of_operation + " " + "Sun Closed"
                hours_of_operation = (
                    hours_of_operation.replace("1,", "Mon ")
                    .replace("2,", "Tue ")
                    .replace("3,", "Wed ")
                    .replace("4,", "Thu ")
                    .replace("5,", "Fri ")
                    .replace("6,", "Sat ")
                    .replace("7,", "Sun ")
                    .replace(";", " ")
                    .replace(",", "-")
                )
            location_name = loc["name"]
            phone = loc["phone"]
            street_address = loc["address"]
            city = loc["locality"]
            state = loc["region"]
            zip_postal = loc["postcode"]
            country_code = loc["country"]
            latitude = loc["latitude"]
            longitude = loc["longitude"]
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=location_type,
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
