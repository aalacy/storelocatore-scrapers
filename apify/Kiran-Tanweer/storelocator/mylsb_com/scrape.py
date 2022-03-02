from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
import json


session = SgRequests()
website = "mylsb_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

payload = json.dumps(
    {
        "Radius": 5000,
        "Latitude": 42.3255713,
        "Longitude": -92.5792482,
        "Connectors": [
            {
                "name": "Website",
                "selected": True,
                "icon": "map-pin.png",
                "zIndex": 10000,
                "filters": [
                    {"name": "LocationTypeBankingFinancialServices", "selected": False},
                    {
                        "name": "LocationTypeInsuranceTrustWealthManagement",
                        "selected": False,
                    },
                ],
            }
        ],
    }
)
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "Origin": "https://www.mylsb.com",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.mylsb.com/support/resources/locations",
    "Accept-Language": "en-US,en;q=0.9",
    "Cookie": "nmstat=273d8840-ad6e-252b-0a1e-2e0c76a91134; _ga=GA1.2.1308971789.1636134610; _gid=GA1.2.1865825783.1636134610; _gat_UA-2125178-1=1",
}

DOMAIN = "https://www.mylsb.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search_url = "https://www.mylsb.com/Api/Locations/GetLocations"
        stores_req = session.post(search_url, headers=headers, data=payload).json()
        for store in stores_req:
            title = store["name"]
            link = "https://www.mylsb.com" + store["kenticoUrl"]
            lat = store["latitude"]
            lng = store["longitude"]
            street = store["address1"] + " " + store["address2"]
            city = store["city"]
            state = store["state"]
            pcode = store["zipCode"]
            phone = store["phone"]
            hours = store["hours"]
            hours = BeautifulSoup(hours, features="lxml")
            hours = hours.text
            hours = hours.split("\n")[1]
            hours = hours.split("Drive-Thru Hours")[0]

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode,
                country_code="US",
                store_number=MISSING,
                phone=phone,
                location_type=MISSING,
                latitude=lat,
                longitude=lng,
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
