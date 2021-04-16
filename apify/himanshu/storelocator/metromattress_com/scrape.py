import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter


session = SgRequests()
website = "metromattress.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }
    name_list = []
    for q in range(11):
        base_url = "https://www.metromattress.com/locationsmain/" + str(q) + "/"
        r = session.get(base_url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("h2", {"class": "wppl-h2"})
        for loc in loclist:
            page_url = loc.find("a")["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            location_name = soup.find("h1").text
            if location_name in name_list:
                continue
            name_list.append(location_name)
            temp = soup.find("div", {"class": "medium-3 columns"})
            hours_of_operation = temp.text.split("HOURS")[1]
            temp = temp.find("p")
            address = temp.get_text(separator="|", strip=True).split("|")
            if len(address) < 3:
                address = temp.text.split("\n")
                phone = address[1].split("(")
                address = address[0] + " " + phone[0].strip()
                phone = "(" + phone[1].replace("Call", "")
            else:
                if len(address) > 3:
                    address = address[:-1]
                phone = address[-1].replace("Call", "")
                address = address[0] + " " + address[1].strip()
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
            longitude = (
                soup.find_all("iframe")[2]["src"].split("!2d")[-1].split("!3d")[0]
            )
            latitude = (
                soup.find_all("iframe")[2]["src"]
                .split("!2d")[-1]
                .split("!3d")[1]
                .split("!")[0]
            )
            yield SgRecord(
                locator_domain="https://www.metromattress.com/",
                page_url=page_url,
                location_name=location_name.strip(),
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code="US",
                store_number="<MISSING>",
                phone=phone.strip(),
                location_type="<MISSING>",
                latitude=latitude.strip(),
                longitude=longitude.strip(),
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
