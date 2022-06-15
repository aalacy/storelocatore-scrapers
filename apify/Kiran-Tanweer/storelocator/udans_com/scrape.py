import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "udans.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://udans.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://udans.com/pages/ud-locations"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        linklist = soup.find("div", {"class": "rte"}).findAll("a")
        for link in linklist:
            location_type = MISSING
            link_url = DOMAIN + link["href"]
            log.info(link_url)
            r = session.get(link_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            loclist = soup.findAll("div", {"class": "store-info-floating-box"})
            for loc in loclist:
                location_name = loc.find("h3").text
                log.info(location_name)
                address = loc.find("p")
                phone = soup.select_one("a[href*=tel]").text
                longitude, latitude = (
                    soup.find("span", {"itemprop": "map"})
                    .text.split("!2d", 1)[1]
                    .split("!2m", 1)[0]
                    .split("!3d")
                )
                hours_of_operation = (
                    loc.find("div", {"class": "regular-hours"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                    .replace("Regular Hours :", "")
                )
                if "Will reopen" in address:
                    location_type = "Temporarily Closed"
                    hours_of_operation = MISSING
                    address = loc.findAll("p")[1]
                if "," not in address.text:
                    address = loc.findAll("p")[1]
                address = address.get_text(separator="|", strip=True).replace("|", " ")
                if "!3m" in latitude:
                    latitude = latitude.split("!3m")[0]
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
                phone = soup.select_one("a[href*=tel]").text
                country_code = "US"
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
                    location_type=location_type,
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
