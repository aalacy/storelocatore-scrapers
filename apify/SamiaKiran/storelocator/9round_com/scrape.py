import json
import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "9round_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    if True:
        url = "https://www.9round.com/locations/directory"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("li", {"class": "pb-1"})
        for loc in loclist:
            url = "https://www.9round.com" + loc.find("a")["href"]
            r = session.get(url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            state_list = soup.findAll("a", {"class": "lead"})
            for link in state_list:
                page_url = "https://www.9round.com" + link["href"]
                r = session.get(page_url, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                try:
                    temp = r.text.split("<script type='application/ld+json'>")[1].split(
                        "</script>", 1
                    )[0]
                except:
                    continue
                log.info(page_url)
                temp = json.loads(temp)
                location_name = temp["name"]

                latitude = temp["geo"]["latitude"]
                longitude = temp["geo"]["longitude"]
                hours_of_operation = temp["openingHours"]
                try:
                    phone = soup.select_one("a[href*=tel]").text.replace("\n", "")
                except:
                    phone = "<MISSING>"
                try:
                    address = (
                        soup.find("h4", {"class": "h4-responsive font-weight-bolder"})
                        .get_text(separator="|", strip=True)
                        .replace("|", " ")
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
                except:
                    street_address = temp["address"]["streetAddress"]
                    city = temp["address"]["addressLocality"]
                    state = temp["address"]["addressRegion"]
                    zip_postal = temp["address"]["postalCode"]
                yield SgRecord(
                    locator_domain="https://www.9round.com/",
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
