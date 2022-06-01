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
website = "codysoriginalroadhouse_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "http://codysoriginalroadhouse.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "http://codysoriginalroadhouse.com/locations.html"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "clearfix grpelem"}).find_all(
            "a", {"class": "nonblock nontext grpelem"}
        )
        for loc in loclist:
            page_url = DOMAIN + loc["href"]
            if "index" in page_url:
                continue
            elif "drink" in page_url:
                continue
            elif "menu" in page_url:
                continue
            elif "facebook" in page_url:
                continue
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            location_details = (
                soup.find("div", {"class": "clearfix colelem", "id": re.compile("-")})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            location_details = location_details.split("Phone:")
            address = location_details[0]
            location_details = location_details[1].split("Hours of Operation:")
            phone = location_details[0]
            hours_of_operation = location_details[1]
            coords = soup.select_one("iframe[src*=maps]")["src"]
            try:
                longitude, latitude = (
                    coords.split("!2d", 1)[1].split("!2m", 1)[0].split("!3d")
                )
            except:
                longitude, latitude = (
                    coords.split("ll=", 1)[1].split("&", 1)[0].split(",")
                )
            if "!3m" in latitude:
                latitude = latitude.split("!3m")[0]
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
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=MISSING,
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
