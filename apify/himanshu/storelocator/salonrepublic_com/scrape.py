import json
import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "salonrepublic_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


DOMAIN = "https://salonrepublic.com/"
MISSING = "<MISSING>"


def fetch_data():
    url = "https://salonrepublic.com/locations/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    loclist = soup.find("div", {"class": "pt-cv-view pt-cv-grid pt-cv-colsys"}).findAll(
        "div", {"class": "pt-cv-ifield"}
    )
    for loc in loclist:
        page_url = loc.find("a")["href"]
        log.info(page_url)
        r = session.get(page_url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        try:
            temp = r.text.split('<script type="application/ld+json">')[1].split(
                "</script>"
            )[0]
        except:
            continue
        temp = json.loads(temp)
        location_name = temp["name"]
        address = temp["address"]
        street_address = address["streetAddress"].replace(")", "")
        city = address["addressLocality"]
        state = address["addressRegion"]
        zip_postal = address["postalCode"]
        country_code = "US"
        try:
            hours_of_operation = (
                str(temp["openingHours"])
                .replace("['", "")
                .replace("]'", "")
                .replace("']", "")
            )

        except:
            hours_of_operation = MISSING
        r = session.get(page_url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        temp_list = soup.find("div", {"id": "loc_header"})
        location_name = temp_list.find("h1").text
        phone = temp_list.select_one("a[href*=tel]").text
        address = (
            soup.find("p", {"class": "loc_address"})
            .get_text(separator="|", strip=True)
            .replace("|", " ")
        )
        address = (
            address.replace(",", " ")
            .replace("Private street level entrance", "")
            .replace("located in Westfield Town Center", "")
            .replace("located in The Paseo", "")
        )
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
            location_name=location_name.strip(),
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
