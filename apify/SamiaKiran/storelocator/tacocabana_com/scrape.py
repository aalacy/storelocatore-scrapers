import json
import time
import re
from sglogging import sglog
from sgselenium import SgChrome
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "tacocabana_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    with SgChrome() as driver:
        driver.get("https://www.tacocabana.com/locations")
        time.sleep(25)
        driver.find_element_by_xpath(
            "//button[contains(., 'view all locations')]"
        ).click()
        time.sleep(50)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        loclist = soup.findAll(
            "div", {"class": "card-info styles__StyledCardInfo-s1y7dfjk-3 gCNPSz"}
        )
    r = session.get("https://www.tacocabana.com/locations", headers=headers)
    temp_r = r.text.split(',"list":')[1].split(',"detail"', 1)[0]
    cleanr = re.compile(r"<[^>]+>")
    pattern = re.compile(r"\s\s+")
    for loc in loclist:
        location_name = loc.find("h3")
        location_name = location_name.find("a").text
        log.info(location_name)
        store_number = location_name.split("#", 1)[1]
        address = loc.find("p")
        address = re.sub(cleanr, "\n", str(address))
        address = re.sub(pattern, "\n", address)
        content = address.splitlines()
        if len(content) == 7:
            street_address = " ".join(content[1:3])
            street_address = street_address.replace("&amp;", "&")
            city = content[3]
            state = content[4]
            zip_postal = content[5]
            phone = content[6]
        elif len(content) == 4:
            street_address = content[1]
            street_address = street_address.replace("&amp;", "&")
            temp = content[2].split()
            if len(temp) == 4:
                city = " ".join(temp[0:2])
                state = temp[2]
                zip_postal = temp[3]
            else:
                city = temp[0]
                state = temp[1]
                zip_postal = temp[2]
            phone = content[3]
        elif len(content) == 5:
            try:
                street_address = content[2]
                street_address = street_address.replace("&amp;", "&")
                temp = content[3].split()
                city = temp[0]
                state = temp[1]
                zip_postal = temp[2]
                phone = content[4]
            except:
                street_address = content[1]
                street_address = street_address.replace("&amp;", "&")
                city = content[2]
                temp = content[3].split()
                state = temp[0]
                zip_postal = temp[1]
                phone = content[4]
        else:
            street_address = content[1]
            street_address = street_address.replace("&amp;", "&")
            city = content[2]
            state = content[3]
            zip_postal = content[4]
            phone = content[5]
        try:
            hours_of_operation = loc.text.split(")", 1)[1]
            hours_of_operation = hours_of_operation.split("O", 1)[1]
            hours_of_operation = "O" + hours_of_operation
        except:
            hours_of_operation = "<MISSING>"
        temp_list = json.loads(temp_r)
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        for temp in temp_list:
            if temp["brand_id"] == store_number:
                latitude = temp["latitude"]
                longitude = temp["longitude"]

        yield SgRecord(
            locator_domain="https://www.tacocabana.com/",
            page_url="https://www.tacocabana.com/locations",
            location_name=location_name.strip(),
            street_address=street_address,
            city=city.strip(),
            state=state,
            zip_postal=zip_postal,
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
