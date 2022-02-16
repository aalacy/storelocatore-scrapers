import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

session = SgRequests()
website = "tacobueno_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://tacobueno.com"
MISSING = SgRecord.MISSING


def fetch_data():
    zips = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_results=15,
        expected_search_radius_miles=50,
    )
    if True:
        for zip_code in zips:
            log.info(f"{zip_code} | remaining: {zips.items_remaining()}")
            search_url = "https://www.tacobueno.com/locations/&zip=" + zip_code
            stores_req = session.get(search_url, headers=headers)
            soup = BeautifulSoup(stores_req.text, "html.parser")
            loclist = soup.findAll("div", {"class": "map-listing_item active"})
            for loc in loclist:
                location_type = MISSING
                location_name = loc.find("h2").text
                log.info(location_name)
                if "Temporarily Closed" in location_name:
                    location_type = "Temporarily Closed"
                store_number = location_name.split("-", 1)[1].strip()
                if "-" in store_number:
                    store_number = store_number.split("-", 1)[0]
                address = loc.find("address").text
                temp = location_name.replace("-", "")
                temp = " ".join(temp.split())
                temp = "Call" + " " + temp
                phone = loc.find("a").text
                if not phone:
                    phone = MISSING
                gps = loc.get("data-gps").split(",")
                latitude = gps[0]
                longitude = gps[1]
                country_code = "US"
                hour_list = loc.find("ul").findAll(
                    "li", {"class": "list-toggle-item inactive"}
                )
                hours_of_operation = ""
                for hour in hour_list:
                    hours_of_operation = hours_of_operation + " " + hour.text
                address = address.replace(",", " ")
                address = usaddress.parse(address)
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

                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url="https://www.tacobueno.com/locations/",
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            record_id=RecommendedRecordIds.StoreNumberId,
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
