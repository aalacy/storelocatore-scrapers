import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "extraspace_com "
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://www.extraspace.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.extraspace.com/storage/facilities/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        statelist = soup.find("div", {"class": "light-gray"}).findAll("a")
        for state in statelist:
            stiteMap_url = "https://www.extraspace.com" + state["href"]
            r = session.get(stiteMap_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            loclist = soup.findAll("a", {"class": "electric-gray"})
            for loc in loclist:
                page_url = "https://www.extraspace.com" + loc["href"]
                log.info(page_url)
                r = session.get(page_url, headers=headers, timeout=15)
                soup = BeautifulSoup(r.text, "html.parser")
                try:
                    address = (
                        soup.find("div", {"class": "address-info"})
                        .get_text(separator="|", strip=True)
                        .replace("|", " ")
                    )
                except:
                    continue
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
                location_name = soup.find("h1").text
                temp = soup.find("div", {"class": "phone-container"})
                phone = (
                    soup.find("div", {"class": "current-customer-container"})
                    .find("a")
                    .text
                )
                hours_of_operation = (
                    soup.find("div", {"class": "office-hours"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                    .replace("Office Hours", "")
                )
                try:
                    latitude = r.text.split('"latitude": "')[1].split('"')[0]
                    longitude = r.text.split('"longitude": "')[1].split('"')[0]
                except:
                    latitude = r.text.split('"latitude":')[1].split('"')[0]
                    longitude = r.text.split('"longitude":')[1].split('"')[0]
                store_number = MISSING
                hours_of_operation = hours_of_operation.replace("Storage", "")
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
                    store_number=store_number,
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
