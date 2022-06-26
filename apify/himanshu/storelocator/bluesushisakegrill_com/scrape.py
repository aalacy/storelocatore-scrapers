import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "bluesushisakegrill.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://bluesushisakegrill.com"
MISSING = SgRecord.MISSING


def fetch_data():
    get_url = "https://bluesushisakegrill.com/locations"
    r = session.get(get_url)
    soup = BeautifulSoup(r.text, "html.parser")
    main = soup.find_all("h3", {"class": "locations-item-title"})
    for i in main:
        location_name = i.find("a").text
        page_url = i.find("a")["href"]
        log.info(page_url)
        r1 = session.get(page_url)
        soup1 = BeautifulSoup(r1.text, "html.parser")
        if "coming soon" in soup1.h1.text.lower():
            continue
        address = (
            soup1.find("div", {"class": "location_details-address"})
            .find("p")
            .get_text(separator="|", strip=True)
            .replace("|", " ")
            .replace("flagship_locationselect_color", "")
        )
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
        country_code = "US"
        temp = soup1.select_one("a[href*=maps]")["href"]
        if "@" in temp:
            coords = temp.split("@")[1].split(",")
        else:
            coords = temp.split("&ll=3")[1].split("+")
        latitude = coords[0]
        longitude = coords[1]
        phone = soup1.find("p", {"class": "location_details-phone"}).text.strip()
        hours_of_operation = (
            soup1.find("div", {"class": "location_details-hours"})
            .get_text(separator="|", strip=True)
            .replace("|", " ")
            .rstrip(":")
            .replace("NOW OPEN!", "")
        )
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=MISSING,
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
