import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "mysteryroom_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://mysteryroom.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    res = session.get("https://mysteryroom.com/location/")
    soup = BeautifulSoup(res.text, "html.parser")
    sa = soup.find("div", {"class": "block sectioned-content"}).find_all("a")
    for a in sa:
        location_type = MISSING
        if "https://mysteryroom.com" in a.get("href"):
            page_url = a.get("href")
        else:
            page_url = "https://mysteryroom.com" + a.get("href").replace(
                "https://allinadventures.com", ""
            )
        log.info(page_url)
        res = session.get(page_url)
        if "temporarily CLOSED" in res.text:
            location_type = "Temporarily CLOSED"
        soup = BeautifulSoup(res.text, "html.parser")
        location_name = soup.find("h1").text
        phone = (
            soup.find("span", {"id": "phone-1"})
            .text.replace("Click here to call ", "")
            .strip()
        )
        try:
            address = (
                soup.find("span", {"id": "location-1"})
                .text.replace("Click here to view location ", "")
                .strip()
            )
        except:
            address = location_name.replace("– TBD", "")
        address = address.replace(",", " ").replace("\n", " ")
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
        try:
            hours_of_operation = (
                soup.findAll("div", {"class": "col-inner"})[1]
                .find("ul")
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
        except:
            hours_of_operation = MISSING
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
            location_type=location_type,
            latitude=MISSING,
            longitude=MISSING,
            hours_of_operation=hours_of_operation.strip(),
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
