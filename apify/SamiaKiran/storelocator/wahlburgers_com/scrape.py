from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape import sgpostal as parser


website = "wahlburgers_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    if True:
        url = "https://wahlburgers.com/all-locations"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        linklist = soup.find("div", {"class": "cell medium-6"}).findAll("a")
        for link in linklist:
            page_url = "https://wahlburgers.com" + link["href"]
            log.info(page_url)
            if "Coming soon" in page_url:
                continue
            if "canada" in page_url:
                country_code = "Canada"
            elif "germany" in page_url:
                country_code = "Germany"
            else:
                country_code = "USA"
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            loclist = soup.find("div", {"class": "cell"}).findAll(
                "a", {"class": "fadey"}
            )
            for loc in loclist:
                try:
                    page_url = "https://wahlburgers.com" + loc["href"]
                    r = session.get(page_url, headers=headers)
                    if "Coming soon" in r.text:
                        continue
                    soup = BeautifulSoup(r.text, "html.parser")
                    temp = soup.find("div", {"class": "insideThing"}).findAll("div")
                    if "We are currently closed" in r.text:
                        location_type = "Temporarily Closed"
                    else:
                        location_type = "<MISSING>"
                except:
                    continue
                log.info(page_url)
                location_name = (
                    soup.find("div", {"class": "location whitepage"})
                    .find("h1")
                    .text.replace("@", "")
                    .replace("\n", "")
                    .split()
                )
                location_name = " ".join(x for x in location_name)
                if "General Manager:" in temp[-1].text:
                    del temp[-1]
                if len(temp) > 3:
                    temp = temp[1:]
                try:
                    phone = (
                        temp[0].find("a")["href"].replace("tel:", "").replace("%20", "")
                    )
                    hours_of_operation = (
                        temp[2].get_text(separator="|", strip=True).replace("|", " ")
                    ).replace("Opening hours:", "")
                    address = temp[1].get_text(separator="|", strip=True).split("|")[1:]
                except:
                    phone = "<MISSING>"
                    hours_of_operation = (
                        temp[1].get_text(separator="|", strip=True).replace("|", " ")
                    ).replace("Opening hours:", "")
                    address = temp[0].get_text(separator="|", strip=True).split("|")[1:]
                address = " ".join(
                    x.replace("\n", "").replace("    ", " ") for x in address
                )
                formatted_addr = parser.parse_address_intl(address)
                street_address = formatted_addr.street_address_1
                if street_address is None:
                    street_address = formatted_addr.street_address_2
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )
                city = formatted_addr.city
                state = formatted_addr.state if formatted_addr.state else "<MISSING>"
                zip_postal = formatted_addr.postcode
                coords = soup.select_one("iframe[src*=maps]")["src"]
                r = session.get(coords, headers=headers)
                coords = r.text.split("null,[null,null,")[2].split("],")[0].split(",")
                latitude = coords[0]
                longitude = coords[1]
                yield SgRecord(
                    locator_domain="https://wahlburgers.com/",
                    page_url=page_url,
                    location_name=location_name.strip(),
                    street_address=street_address.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=zip_postal.strip(),
                    country_code=country_code,
                    store_number="<MISSING>",
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude.strip(),
                    longitude=longitude.strip(),
                    hours_of_operation=hours_of_operation.strip(),
                    raw_address=address,
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
