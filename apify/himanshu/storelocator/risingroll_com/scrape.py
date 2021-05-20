import re
import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter


website = "risingroll_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    if True:
        url = "https://risingroll.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"id": "locdesc"})
        for loc in loclist:
            page_url = "https://risingroll.com" + loc.find("a")["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            location_name = (
                soup.find("div", {"class": "header-content"}).find("h1").text
            )
            temp = (
                soup.findAll("div", {"class": "et_pb_text_inner"})[1]
                .get_text(separator="|", strip=True)
                .split("|")[1:]
            )
            for i, s in enumerate(temp):
                if "Owner:" in s:
                    indice = i
                elif "Owners:" in s:
                    indice = i
            address = temp[:indice]
            temp_address = address[-1].split()
            if temp_address[-1].isdigit() and len(temp_address[-1]) == 5:
                if "University" in address[1]:
                    address = address[2:]
            else:
                del address[-1]
            address = " ".join(x for x in address)
            latitude, longitude = (
                soup.find("iframe", {"src": re.compile("mapquest.com")})["src"]
                .split("center=", 1)[1]
                .split("&zoom=", 1)[0]
                .split(",")
            )
            indice = indice + 1
            temp = " ".join(x for x in temp[indice:])
            try:
                hours_of_operation = temp.split("Open:", 1)[1]
                if "We are following" in hours_of_operation:
                    hours_of_operation = hours_of_operation.split(
                        "We are following", 1
                    )[0]
                elif "The health and safety" in hours_of_operation:
                    hours_of_operation = hours_of_operation.split(
                        "The health and safety", 1
                    )[0]
                elif "Breakfast" in hours_of_operation:
                    hours_of_operation = hours_of_operation.split("Breakfast", 1)[0]
                else:
                    hours_of_operation = hours_of_operation.split("Lunch", 1)[0]

            except:
                hours_of_operation = "<MISSING>"
            try:
                phone = temp.split("P:", 1)[1].split()[0]
            except:
                try:
                    phone = temp.split("T: ")[1]
                except:
                    try:
                        phone = temp.split("P :")[1]
                    except:
                        phone = "<MISSING>"
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

            yield SgRecord(
                locator_domain="https://risingroll.com/",
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
