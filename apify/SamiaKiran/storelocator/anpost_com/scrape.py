from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "anpost_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

DOMAIN = "https://www.anpost.com/"
MISSING = SgRecord.MISSING


url = "https://www.anpost.com/AnPost/StoreLocatorServices.asmx/Search?name=%27%27&radius=5&userLat=53.34933275&userLon=-6.26065885&service=%27%27&type=%27POST%20OFFICE%27"
headers = {
    "authority": "www.anpost.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json;charset=utf-8",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.anpost.com/",
    "accept-language": "en-US,en;q=0.9",
}


def fetch_data():
    if True:
        loclist = session.get(url, headers=headers).json()["d"]
        for loc in loclist:
            location_name = loc["Name"]
            log.info(location_name)
            store_number = loc["Id"]
            phone = loc["Phone"]
            street_address = loc["Address2"]
            log.info(street_address)
            city = loc["Town"]
            state = loc["County"]
            zip_postal = loc["EirCode"]
            country_code = "Ireland"
            latitude = loc["Latitude"]
            longitude = loc["Longitude"]
            hours_of_operation = loc["OpeningHours"]
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url="https://www.anpost.com/#storelocator",
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
                hours_of_operation=hours_of_operation,
            )


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
