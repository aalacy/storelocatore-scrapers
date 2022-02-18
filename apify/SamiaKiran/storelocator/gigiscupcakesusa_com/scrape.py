from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "gigiscupcakesusa_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://gigiscupcakesusa.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://easylocator.net/ajax/search_by_lat_lon_geojson/gigiscupcakesusa/24.9056/67.0822/0/50"
        loclist = session.get(url, headers=headers).json()["physical"]
        for loc in loclist:
            store_number = loc["properties"]["location_number"]
            location_name = loc["properties"]["name"]
            page_url = loc["properties"]["website_url"]
            log.info(location_name)
            if not page_url:
                page_url = "https://gigiscupcakesusa.com/pages/stores-in-store-pickup"
            street_address = loc["properties"]["street_address"]
            city = loc["properties"]["city"]
            state = loc["properties"]["state_province"]
            zip_postal = loc["properties"]["zip_postal_code"]
            phone = loc["properties"]["phone"]
            if not phone:
                r = session.get(page_url, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                phone = soup.findAll("p")
                phone = (
                    phone[2]
                    .get_text(separator="|", strip=True)
                    .split("|")[0]
                    .replace("Phone:", "")
                )
            hours_of_operation = loc["properties"]["additional_info"]
            hours_of_operation = (
                BeautifulSoup(hours_of_operation, "html.parser")
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            latitude = loc["properties"]["lat"]
            longitude = loc["properties"]["lon"]
            country_code = "US"
            if not street_address:
                r = session.get(page_url, headers=headers)
                temp = r.text.split('<div class="content__head">')[1].split("</div>")[0]
                soup = BeautifulSoup(temp, "html.parser")
                loc = soup.findAll("p")
                address = loc[0].get_text(separator="|", strip=True).split("|")
                street_address = address[0]
                address = address[1].split(",")
                city = address[0]
                address = address[1].split()
                state = address[0]
                zip_postal = address[1]
                phone = (
                    loc[2]
                    .get_text(separator="|", strip=True)
                    .split("|")[0]
                    .replace("Phone:", "")
                )
                hours_of_operation = loc[3].text + " " + loc[4].text + " " + loc[5].text
            hours_of_operation = hours_of_operation.replace("Closed due to Covid19", "")
            if "Order for" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("Order for")[0]
            location_type = MISSING
            if "Temporarily Closed Please visit " in hours_of_operation:
                location_type = "Temporarily Closed"
                hours_of_operation = MISSING
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
