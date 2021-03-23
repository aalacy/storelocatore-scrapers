from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "petsuitesofamerica_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    final_data = []
    url = "https://liveapi.yext.com/v2/accounts/me/entities?filter=%7B%20%22meta.folderId%22%3A%7B%22%24in%22%3A[249017]%7D%7D&limit=50&api_key=2bc9758495549d8bd15fe1c10fdcd617&v=20161012"
    loclist = session.get(url, headers=headers).json()["response"]["entities"]
    for loc in loclist:
        try:
            page_url = loc["c_baseURL"]
        except:
            page_url = "<MISSING>"
        try:
            location_name = loc["facebookName"]
        except:
            location_name = loc["name"]
        street_address = loc["address"]["line1"]
        city = loc["address"]["city"]
        state = loc["address"]["region"]
        zip_postal = loc["address"]["postalCode"]
        country_code = loc["address"]["countryCode"]
        latitude = loc["cityCoordinate"]["latitude"]
        longitude = loc["cityCoordinate"]["longitude"]
        log.info(page_url)
        try:
            phone = loc["c_websitePhone"]
        except:
            phone = loc["mainPhone"]
        try:
            store_number = loc["c_websiteID"]
        except:
            store_number = "<MISSING>"
        monday = loc["hours"]["monday"]["openIntervals"][0]
        monday_s = monday["start"]
        monday_e = monday["end"]
        tuesday = loc["hours"]["tuesday"]["openIntervals"][0]
        tuesday_s = tuesday["start"]
        tuesday_e = tuesday["end"]
        wednesday = loc["hours"]["wednesday"]["openIntervals"][0]
        wednesday_s = wednesday["start"]
        wednesday_e = wednesday["end"]
        thursday = loc["hours"]["thursday"]["openIntervals"][0]
        thursday_s = thursday["start"]
        thursday_e = thursday["end"]
        friday = loc["hours"]["friday"]["openIntervals"][0]
        friday_s = friday["start"]
        friday_e = friday["end"]
        saturday = loc["hours"]["saturday"]["openIntervals"][0]
        saturday_s = saturday["start"]
        saturday_e = saturday["end"]
        sunday = loc["hours"]["sunday"]["openIntervals"][0]
        sunday_s = sunday["start"]
        sunday_e = sunday["end"]
        mon = "Mon " + monday_s + "-" + monday_e
        tue = "Tue " + monday_s + "-" + monday_e
        wed = "Wed " + monday_s + "-" + monday_e
        thu = "Thu " + monday_s + "-" + monday_e
        fri = "Fri " + monday_s + "-" + monday_e
        sat = "Sat " + monday_s + "-" + monday_e
        sun = "Sun " + monday_s + "-" + monday_e
        hours_of_operation = (
            mon + " " + tue + " " + wed + " " + thu + " " + fri + " " + sat + " " + sun
        )
        yield SgRecord(
            locator_domain="https://www.petsuitesofamerica.com/",
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code=country_code,
            store_number="<MISSING>",
            phone=phone,
            location_type="<MISSING>",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
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
