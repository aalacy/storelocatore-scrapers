import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "greatwraps.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.greatwraps.com"
MISSING = SgRecord.MISSING


def fetch_data():
    url = "https://www.greatwraps.com/locations-list/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.findAll("a", {"class": "textlink"})
    for link in linklist:
        page_url = "https://www.greatwraps.com" + link["href"]
        log.info(page_url)
        r = session.get(page_url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        location_name = soup.find("div", {"id": "locName"}).text
        phone = soup.find("div", {"id": "locPhone"}).text
        address = soup.find("p", {"class": "locationsAddress"}).text
        address = address.replace(",", " ").replace("USA", "")
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
        hours_of_operation = (
            soup.find("div", {"id": "locationsHours"})
            .get_text(separator="|", strip=True)
            .replace("|", " ")
            .replace("Hours of Operation", "")
        )
        latitude, longitude = (
            r.text.split("var latlng = new google.maps.LatLng(")[1]
            .split(")")[0]
            .split(",")
        )
        country_code = "US"
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
