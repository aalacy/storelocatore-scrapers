import html
import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "flipperspizzeria_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://flipperspizzeria.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://flipperspizzeria.com/wp-json/wp/v2/posts?per_page=100"
        loclist = session.get(url, headers=headers).json()
        for loc in loclist:
            page_url = "https://flipperspizzeria.com/" + loc["slug"]
            store_number = loc["id"]
            log.info(page_url)
            location_name = loc["title"]["rendered"]
            location_name = html.unescape(location_name)
            phone = loc["acf"]["phone_number"]
            address = loc["acf"]["map_address"]["address"]
            address = BeautifulSoup(address, "html.parser")
            address = address.get_text(separator="|", strip=True).replace("|", " ")
            if "12525 Florida 535" in address:
                continue
            raw_address = address.replace(",", " ")
            address = usaddress.parse(raw_address)
            i = 0
            street_address = ""
            city = ""
            state = ""
            zip_postal = ""
            while i < len(address):
                temp = address[i]
                if (
                    temp[1].find("Address") != -1
                    or temp[1].find("Street") != -1
                    or temp[1].find("Recipient") != -1
                    or temp[1].find("Occupancy") != -1
                    or temp[1].find("BuildingName") != -1
                    or temp[1].find("USPSBoxType") != -1
                    or temp[1].find("USPSBoxID") != -1
                ):
                    street_address = street_address + " " + temp[0]
                if temp[1].find("PlaceName") != -1:
                    city = city + " " + temp[0]
                if temp[1].find("StateName") != -1:
                    state = state + " " + temp[0]
                if temp[1].find("ZipCode") != -1:
                    zip_postal = zip_postal + " " + temp[0]
                i += 1
            city = city.replace("St Lake Mary", "Lake Mary")
            country_code = "US"
            latitude = loc["acf"]["map_address"]["lat"]
            longitude = loc["acf"]["map_address"]["lng"]
            hours_of_operation = loc["acf"]["hours"]
            hours_of_operation = BeautifulSoup(hours_of_operation, "html.parser")
            hours_of_operation = (
                hours_of_operation.get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Dine-In, Take-Out and Delivery", "")
            )
            if "DELIVERY ONLY" in hours_of_operation:
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
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
                raw_address=raw_address,
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
