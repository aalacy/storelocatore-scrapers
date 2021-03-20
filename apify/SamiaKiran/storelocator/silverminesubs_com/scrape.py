import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "silverminesubs_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    temp = []
    if True:
        url = "https://www.silverminesubs.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "storerow"})
        for loc in loclist:
            location_name = loc.find("div", {"class": "storename inlineblock"}).text
            page_url = loc.find("div", {"class": "storename inlineblock"}).find("a")[
                "href"
            ]
            phone = loc.find("div", {"class": "storephone inlineblock"}).text
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            if "Page not found" in r.text:
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            temp = soup.findAll("div", {"class": "storesideblock"})
            try:
                hours_of_operation = (
                    temp[2].get_text(separator="|", strip=True).split("|")
                )
                hours_of_operation = hours_of_operation[1] + " " + hours_of_operation[2]
            except:
                try:
                    hours_of_operation = temp[2].text.replace("Hours", "")
                except:
                    hours_of_operation = "<MISSING>"
            try:
                address = temp[0].text.replace("Address", "").replace("\n", "").strip()
                address = address.replace(",", "")
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

            except:
                link = soup.find("iframe")["src"]
                r = session.get(link, headers=headers)
                address = (
                    r.text.split("Silver Mine Subs,")[1]
                    .split("],", 1)[0]
                    .replace("[", "")
                    .split(",")
                )
                street_address = address[0]
                city = address[1]
                address = address[2].strip().split()
                state = address[0].strip()
                zip_postal = address[1]
            coords = soup.find("iframe")["src"]
            try:
                latitude, longitude = (
                    coords.split("sll=")[1].split("&amp;", 1)[0].split(",") & sspn
                )
            except:
                try:
                    latitude, longitude = (
                        coords.split("!1d", 1)[1].split("!3d", 1)[0].split("!2d")
                    )
                    latitude = latitude[2:]
                except:
                    latitude, longitude = (
                        coords.split("sll=")[1].split("&sspn", 1)[0].split(",")
                    )
            yield SgRecord(
                locator_domain="https://www.silverminesubs.com/",
                page_url=page_url,
                location_name=location_name,
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
                hours_of_operation=hours_of_operation.replace("NEW HOURS", "").strip(),
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
