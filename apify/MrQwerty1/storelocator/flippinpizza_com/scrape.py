import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "flippinpizza_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://flippinpizza.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://flippinpizza.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("item")
        for loc in loclist:
            location_name = loc.find("location").text.replace("&#44;", "")
            page_url = loc.find("exturl").text
            latitude = loc.find("latitude").text
            longitude = loc.find("longitude").text
            phone = loc.find("telephone").text
            if not page_url:
                temp = BeautifulSoup(loc.find("description").text, "html.parser")
                page_url = temp.findAll("a")[-1]["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            if "Coming soon" in soup.find("h1").text:
                continue
            if not phone:
                phone = (
                    soup.find("div", {"class": "location-address"})
                    .findAll("p")[3]
                    .text.replace("PHONE:", "")
                )
            if not phone:
                phone = soup.select_one("a[href*=tel]").text
            try:
                hour_url = soup.find("div", {"class": "hours-btn"}).find("a")["href"]
                log.info("Fetching Hours...")
                r = session.get(hour_url, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                hours_of_operation = (
                    soup.find("table")
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
            except:
                try:
                    hour_url = soup.find("div", {"class": "hours-btn"}).text
                    if "Coming soon" in hour_url:
                        hours_of_operation = MISSING
                except:
                    hours_of_operation = soup.find(
                        "div", {"class": "location-address"}
                    ).findAll("em")
                    hours_of_operation = " ".join(x.text for x in hours_of_operation)
            address = loc.find("address").text
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
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
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
