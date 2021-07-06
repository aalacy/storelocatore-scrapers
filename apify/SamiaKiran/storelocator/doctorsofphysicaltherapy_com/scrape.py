import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "doctorsofphysicaltherapy_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://doctorsofphysicaltherapy.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://doctorsofphysicaltherapy.com/our-locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        linklist = soup.findAll("div", {"class": "row"})[1].findAll("p")
        for link in linklist[4:-1]:
            try:
                page_url = link.find("a")["href"]
                log.info(page_url)
                r = session.get(page_url, headers=headers)
                if r.status_code == 404:
                    continue
                soup = BeautifulSoup(r.text, "html.parser")
                temp = soup.find("div", {"class": "wpsl-locations-details"})
                location_name = temp.find("strong").text
                address = (
                    temp.find("div", {"class": "wpsl-location-address"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                    .replace("United States", "")
                )
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
                phone = (
                    soup.find("div", {"class": "wpsl-contact-details"}).find("a").text
                )
                hour_list = soup.find("table", {"class": "wpsl-opening-hours"}).findAll(
                    "tr"
                )
                hours_of_operation = ""
                for hour in hour_list:
                    temp = hour.findAll("td")
                    day = temp[0].text
                    time = temp[1].text
                    hours_of_operation = hours_of_operation + " " + day + " " + time
            except:
                hours_of_operation = MISSING
                page_url = url
                temp = link.get_text(separator="|", strip=True).split("|")
                if "P.O. Box" in temp[2]:
                    del temp[2]
                location_name = temp[0]
                street_address = temp[1]
                address = temp[2].split(",")
                phone = temp[3].replace("P:", "")
                city = address[0]
                address = address[1].split()
                state = address[0]
                zip_postal = address[1]
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
