from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "foreyes.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    url = "https://www.foreyes.com/locations/location/ajax?lat=25.73762393580607&lng=-80.65977249296874&ne=62.95639695152038%2C-24.385596663458678&sw=-27.181502311207137%2C-137.37723484705242&rad=max"
    loclist = session.get(url, headers=headers).json()["items"]
    for store_data in loclist:
        location_name = store_data["store_name"]
        page_url = store_data["url_key"]
        page_url = "https://www.foreyes.com/locations/" + page_url
        log.info(page_url)
        street_address = store_data["store_address_line"]
        city = store_data["store_city"]
        state = store_data["store_state"]
        zip_postal = store_data["store_zip"]
        store_number = store_data["sofe_store_id"]
        phone = store_data["store_phone"]
        location_type = store_data["store_type"]
        latitude = store_data["store_lat"]
        longitude = store_data["store_long"]
        r = session.get(page_url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        hour_list = soup.find("div", {"class": "address hours"}).findAll("tr")
        hours_of_operation = ""
        for hour in hour_list:
            hour = hour.findAll("td")
            day = hour[0].text
            time = hour[1].text + "-" + hour[2].text
            hours_of_operation = hours_of_operation + day + " " + time + " "
        yield SgRecord(
            locator_domain="https://foreyes.com/",
            page_url=page_url,
            location_name=location_name,
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code="US",
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
