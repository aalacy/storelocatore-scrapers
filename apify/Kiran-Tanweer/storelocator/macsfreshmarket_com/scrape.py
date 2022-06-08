from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import os


os.environ["PROXY_URL"] = "http://groups-BUYPROXIES94952:{}@proxy.apify.com:8000/"
os.environ["PROXY_PASSWORD"] = "apify_proxy_4j1h689adHSx69RtQ9p5ZbfmGA3kw12p0N2q"

session = SgRequests()
website = "macsfreshmarket_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://macsfreshmarket.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://admin.grocerytech.solutions/api/Stores"
        r = session.get(url, headers=headers).json()
        for loc in r:
            storeid = loc["storeNumber"]
            title = loc["name"]
            address_1 = loc["address1"]
            address_2 = loc["address2"]
            if address_2 is not None:
                street = address_1 + " " + address_2
            else:
                street = address_1
            city = loc["city"]
            state = loc["state"]
            pcode = loc["zipCode"]
            phone = loc["phone"]
            lat = loc["latitude"]
            lng = loc["longitude"]
            hours = loc["hours"]
            if hours is None:
                hours = MISSING
            else:
                hours = hours.replace("\n", " ")
                hours = hours.replace("Open 7 Days:", "")
                hours = hours.replace("Open 7 days:", "")
                hours = hours.replace("7 Days a Week!", "")
                hours = hours.replace("7 Days a Week", "")
                hours = hours.replace("Open 7 Days A Week", "")
                hours = hours.replace(" • 7 Days A Week!", "")
                hours = hours.replace("Save-A-Lot Liquor", "<MISSING>")
                hours = hours.replace("M-S ", "")
                hours = hours.replace("Hours: ", "")
                hours = hours.replace("!", "")
                hours = hours.replace(".", "")
                hours = hours.strip()
                if hours.find("Sat") == -1:
                    hours = "Mon-Sun: " + hours

                hours = hours.replace("Mon-Sun: <MISSING>", "<MISSING>")

            if title.find("Mac's") != -1:

                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=DOMAIN,
                    location_name=title.strip(),
                    street_address=street.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=pcode.strip(),
                    country_code="US",
                    store_number=storeid,
                    phone=phone.strip(),
                    location_type=SgRecord.MISSING,
                    latitude=lat,
                    longitude=lng,
                    hours_of_operation=hours.strip(),
                )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LATITUDE, SgRecord.Headers.LONGITUDE},
                fail_on_empty_id=True,
            )
            .with_truncate(SgRecord.Headers.LATITUDE, 3)
            .with_truncate(SgRecord.Headers.LONGITUDE, 3)
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
