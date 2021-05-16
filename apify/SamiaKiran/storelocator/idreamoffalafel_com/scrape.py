import usaddress
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "idreamoffalafel_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    temp = []
    if True:
        url = "https://www.idreamoffalafel.com/locations/"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("ul", {"class": "locations"}).findAll("li")
        for loc in loclist:
            try:
                address = (
                    loc.find("h3").get_text(separator="|", strip=True).replace("|", " ")
                )
            except:
                continue
            temp = loc.findAll("p")
            del temp[1]
            phone = (
                temp[0].text.replace("</p>", "").replace("</p>", "").replace("T  ", "")
            )
            if len(temp) > 3:
                hours_of_operation = temp[-2].text + " " + temp[-1].text
            else:
                hours_of_operation = temp[-1].text
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
            location_name = "idreamoffalafel" + " " + street_address
            log.info(location_name)
            yield SgRecord(
                locator_domain="https://www.idreamoffalafel.com/",
                page_url="https://www.idreamoffalafel.com/locations/",
                location_name=location_name.strip(),
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code="US",
                store_number="<MISSING>",
                phone=phone.strip(),
                location_type="<MISSING>",
                latitude="<MISSING>",
                longitude="<MISSING>",
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
