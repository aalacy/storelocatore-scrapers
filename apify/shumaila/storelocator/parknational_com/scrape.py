import json
import html
import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter


session = SgRequests()
website = "parknational_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://parknational.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://parknationalbank.com/about/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        page_no = soup.findAll("a", {"class", "page-numbers"})[2].text
        for page in range(1, int(page_no)):
            url = "https://parknationalbank.com/about/locations/page/" + str(page)
            r = session.get(url, headers=headers)
            log.info(url)
            soup = BeautifulSoup(r.text, "html.parser")
            r = r.text.split("var markers =", 1)[1].split("}]")[0]
            r = r + "}]"
            loclist = json.loads(r)
            divlist = soup.findAll("div", {"class": "location-list-result"})
            for div in divlist:
                temp = div.find("h4").find("a")
                location_name = temp.text
                page_url = temp["href"]
                log.info(page_url)
                address = div.find("span", {"class", "branch-address"}).text
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
                    phone = div.select_one("a[href*=tel]").text
                    temp = div.findAll("div", {"class": "col-3-flex"})
                if len(temp) == 2:
                    try:
                        hours_of_operation = temp[0].get_text(separator="|", strip=True)
                    except:
                        hours_of_operation = MISSING
                else:
                    try:
                        hours_of_operation = (
                            temp[0]
                            .get_text(separator="|", strip=True)
                            .replace("|", " ")
                            + " "
                            + temp[1]
                            .get_text(separator="|", strip=True)
                            .replace("|", " ")
                        )
                    except:
                        hours_of_operation = MISSING
                try:
                    branch = temp[-1].find("li", {"class", "feature-branch"}).text
                    atm = temp[-1].find("li", {"class", "feature-atm"}).text
                    location_type = branch + "|" + atm
                except:
                    branch = temp[-1].find("li", {"class", "feature-branch"}).text
                    location_type = branch
                store_number = div.select_one("a[href*=maps]")["class"][1].split("-")[1]
                for loc in loclist:
                    if html.unescape(loc["title"]) == location_name:
                        latitude = loc["lat"]
                        longitude = loc["lng"]
                        break
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
                    location_name=location_name.strip(),
                    street_address=street_address.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=zip_postal.strip(),
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone.strip(),
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
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
