import re
import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "chickensaladchick_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://chickensaladchick.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    pattern = re.compile(r"\s\s+")
    url = "https://www.chickensaladchick.com/locations/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("li", {"class": "location"})
    for div in divlist:
        latitude = div["data-latitude"]
        longitude = div["data-longitude"]
        location_name = div.find("h4").text
        log.info(location_name)
        address = re.sub(pattern, " ", div.find("address").text)
        phone = div.find("div", {"class": "phone"}).text.replace("\n", "")
        address = address.lstrip()
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
        hour = str(div.find("ul", {"class": "hours"})["data-hours"])
        try:
            hours_of_operation = (
                hour.split('"Interval":"')[1].split('"')[0]
                + " "
                + hour.split('"OpenTime":"')[1].split('"')[0]
                + " - "
                + hour.split('"CloseTime":"')[1].split('"')[0]
            )
            location_type = MISSING
        except:
            hours_of_operation = MISSING
            location_type = "Coming Soon"
        page_url = "https://www.chickensaladchick.com" + div["data-href"]
        log.info(page_url)
        store_number = div["data-loc-id"]
        if not street_address:
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            address = (
                soup.find("div", {"class": "address"})
                .find("em")
                .get_text(separator="|", strip=True)
                .split("|")
            )
            street_address = address[0]
            city = address[1]
            zip_postal = address[-1]
            state = address[-2]

        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name.strip(),
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
