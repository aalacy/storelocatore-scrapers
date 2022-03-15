import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "credobeauty_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://credobeauty.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://credobeauty.com/blogs/credo-stores"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "store-article"})
        for loc in loclist[:-1]:
            page_url = DOMAIN + loc.find("a")["href"]
            log.info(page_url)
            location_name = loc.find("h2", {"class": "store-name"}).text
            phone = loc.find("a", {"class": "tel-store"}).text
            temp = loc.find("div", {"class": "address-store"})
            address = temp.get_text(separator="|", strip=True).replace("|", " ")
            address = address.replace(",", " ").replace("The Shops At Legacy West", "")
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
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            hours_of_operation = (
                soup.find("div", {"class": "store-hours"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Store Hours", "")
            )
            coords = (
                r.text.split("var LatLng =")[1]
                .split(".split('@')[1].split(',');')")[0]
                .split("@")[1]
                .split(",")
            )
            latitude = coords[0]
            longitude = coords[1]
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
