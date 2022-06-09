import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "firstcommercialbk_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.firstcommercialbk.com"
MISSING = SgRecord.MISSING


def fetch_data():
    url = "https://www.firstcommercialbk.com/locations/"
    res = session.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    div = soup.find("div", {"id": "pl-30"})
    locs = str(div).split("<img")[1:]
    for loc in locs:
        loc = BeautifulSoup(loc, "html.parser")
        loc = loc.findAll("p")
        address = loc[0].get_text(separator="|", strip=True).split("|")
        location_name = address[0].replace(":", "")
        log.info(location_name)
        address = " ".join(address[1:])
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
        city = city.replace("Highland Bluff Building", "")
        country_code = "US"
        phone = (
            loc[1]
            .get_text(separator="|", strip=True)
            .split("|")[0]
            .replace("Phone:", "")
        )
        hours_of_operation = (
            loc[2]
            .get_text(separator="|", strip=True)
            .replace("|", " ")
            .replace("Business Hours", "")
            .replace("Lobby", "")
        )
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=MISSING,
            phone=phone,
            location_type=MISSING,
            latitude=MISSING,
            longitude=MISSING,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
