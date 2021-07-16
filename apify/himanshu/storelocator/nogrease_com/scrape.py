import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "nogrease_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://nogrease.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://nogrease.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "col-md-4 center"})
        for loc in loclist:
            address = loc.findAll("address")
            hours_of_operation = (
                address[1]
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Store Hours", "")
                .replace("Store COVID-19 Hours", "")
                .replace(" Appointments are available everyday.", "")
            )
            if "Contact Our School" in hours_of_operation:
                hours_of_operation = MISSING
            try:
                temp_address = address[0].find("strong").text
            except:
                temp_address = ""
            address = address[0].get_text(separator="|", strip=True).split("|")
            if address[0] == temp_address:
                address = address[1:]
            location_name = loc.find("h3").text
            log.info(location_name)
            phone = address[-1]
            if "Suite:" in phone:
                phone = MISSING
                address = " ".join(x for x in address)
            else:
                address = " ".join(x for x in address[:-1])
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
            if "(980" in street_address:
                street_address = street_address.split("(")[0]
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=hours_of_operation.strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
