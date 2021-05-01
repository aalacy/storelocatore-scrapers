import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "chamberlins_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    temp = []
    if True:
        url = "https://chamberlins.com/locations/"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        divlist = soup.find("div", {"class": "container"}).findAll(
            "div", {"class": "row"}
        )[1:]
        for div in divlist:
            loclist = div.findAll("div", {"class": "col-md-6"})
            for loc in loclist:
                temp = loc.find("div", {"class": "locationAddress"}).findAll("p")
                location_name = temp[0].text
                log.info(location_name)
                address = temp[1].get_text(separator="|", strip=True).split("|")
                phone = address[-3].split("Phone:", 1)[1]
                hours_of_operation = address[-2] + " " + address[-1]
                address = address[:-3]
                if "(" in address[2]:
                    del address[2]
                if ")" in address[-1]:
                    del address[-1]
                address = " ".join(x for x in address)
                try:
                    coords = (
                        loc.find("div", {"class": "directionsStyles"})
                        .find("a")["href"]
                        .split("@", 1)[1]
                        .split(",")
                    )
                    latitude = coords[0]
                    longitude = coords[1]
                except:
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
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
                state = state.replace(".", "")

                yield SgRecord(
                    locator_domain="https://chamberlins.com/",
                    page_url="https://chamberlins.com/locations/",
                    location_name=location_name.strip(),
                    street_address=street_address.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=zip_postal.strip(),
                    country_code="US",
                    store_number="<MISSING>",
                    phone=phone,
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
