from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
import os


os.environ["PROXY_URL"] = "http://groups-BUYPROXIES94952:{}@proxy.apify.com:8000/"
os.environ["PROXY_PASSWORD"] = "apify_proxy_4j1h689adHSx69RtQ9p5ZbfmGA3kw12p0N2q"

session = SgRequests()
website = "miguelsrestaurant_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://miguelsrestaurant.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        for i in range(1, 3):
            search_url = "https://miguelsrestaurant.com/locations/?lid=" + str(i)
            stores_req = session.get(search_url, headers=headers)
            soup = BeautifulSoup(stores_req.text, "html.parser")
            soup = str(soup)
            soup = soup.split("locObject.id = " + str(i))[1]
            soup = soup.split("locObject.image =")[0]
            street = soup.split("locObject.address = '")[1].split("';")[0]
            city = soup.split("locObject.city = '")[1].split("';")[0]
            state = soup.split("locObject.state = '")[1].split("';")[0]
            pcode = soup.split("locObject.zip = '")[1].split("';")[0]
            phone = soup.split("locObject.phone = '")[1].split("';")[0]
            coords = soup.split("locObject.latlng = new google.maps.LatLng(")[1].split(
                ");"
            )[0]
            lat, lng = coords.split(", ")
            title = soup.split("locObject.title = '")[1].split("';")[0]
            hours = soup.split("locObject.hours = '")[1].split("';")[0]
            hours = hours.replace("<br />", ", ").strip()
            title = title.replace("&#039;", "'").strip()

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=search_url,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code="US",
                store_number=str(i),
                phone=phone.strip(),
                location_type=MISSING,
                latitude=lat.strip(),
                longitude=lng.strip(),
                hours_of_operation=hours.strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID(
            {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.HOURS_OF_OPERATION}
        )
    )
    with SgWriter(deduper) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
