from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "radiator_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    page_list = []
    url = "https://www.radiator.com/locations"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.find("div", {"id": "locationLinksContainer"}).findAll(
        "div", {"class": "locationLinkContainer"}
    )
    for div in divlist:
        page_url = div.find("a")["href"]
        page_url = "https://www.radiator.com" + page_url
        if page_url in page_list:
            continue
        page_list.append(page_url)
        log.info(page_url)
        r = session.get(page_url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        content = soup.find("div", {"class": "locationContent"})
        if r.status_code == 404 or r.status_code == 400:
            temp = div.get_text(separator="|", strip=True).split("|")
            location_name = temp[0]
            address = temp[1].split("\r\n")
            phone = temp[2]
            street_address = address[0]
            try:
                zip_postal = address[2].strip()
                address = address[1].split(",")
                city = address[0]
                state = address[1]
            except:
                address = temp[1].split("\r\n")
                state = address[1]
                city = address[2].replace(",", "")
                zip_postal = address[3]
            if zip_postal.isdigit():
                country_code = "US"
            else:
                country_code = "CA"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        else:
            temp = div.text.split("|")
            location_name = temp[0]
            phone = temp[-1]
            street_address = (
                content.find("span", {"class": "address-address"}).text
                + " "
                + content.find("span", {"class": "address-address2"}).text
            )
            city = content.find("span", {"class": "address-city"}).text
            state = content.find("span", {"class": "address-state"}).text
            zip_postal = content.find("span", {"class": "address-zip"}).text
            country_code = content.find("span", {"class": "address-country"}).text
            latitude = content.find("input", {"class": "address-latitude"})["value"]
            longitude = content.find("input", {"class": "address-longitude"})["value"]
        yield SgRecord(
            locator_domain="https://radiator.com/",
            page_url=page_url,
            location_name=location_name.strip(),
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code=country_code,
            store_number="<MISSING>",
            phone=phone.strip(),
            location_type="<MISSING>",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation="<MISSING>",
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
