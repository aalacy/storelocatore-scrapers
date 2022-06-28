import ssl
import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgselenium import SgChrome
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

ssl._create_default_https_context = ssl._create_unverified_context

website = "moesitaliansandwiches_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

DOMAIN = "https://www.moesitaliansandwiches.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    with SgChrome() as driver:
        driver.get("https://www.moesitaliansandwiches.com/locations")
        loclist = driver.page_source.split('customMetaTitle":"Menu |')[1:]
        page_list = []
        for loc in loclist:
            page_url = DOMAIN + loc.split('"')[0].lower().strip().replace(" ", "-")
            if page_url in page_list:
                continue
            page_list.append(page_url)
            log.info(page_url)
            driver.get(page_url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            hours_of_operation = (
                soup.find("div", {"class": "hours"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace(
                    "NOW OFFERING CURBSIDE SERVICE & DELIVERY THROUGH DOOR DASH", ""
                )
            )
            if "NOW OFFERING" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("NOW OFFERING")[0]
            elif "ONLINE ORDERING" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("ONLINE ORDERING")[0]
            elif "DELIVERY NOW" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("DELIVERY NOW")[0]
            temp = soup.find("div", {"class": "col-md-6 pm-custom-section-col"})
            location_name = temp.find("h4").text
            temp = temp.findAll("p")
            address = temp[0].get_text(separator="|", strip=True).replace("|", " ")
            phone = temp[1].text
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
                phone=phone,
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
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
