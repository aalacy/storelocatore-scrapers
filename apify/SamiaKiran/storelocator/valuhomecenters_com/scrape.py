import json
import time
from bs4 import BeautifulSoup
from sglogging import sglog
from sgselenium import SgChrome
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "valuhomecenters_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetch_data():
    with SgChrome() as driver:
        url = "https://valuhomecenters.com/store-locator"
        driver.get(url)

        radius = driver.find_element_by_xpath(
            '//*[@id="StoreLocatorForm_Range"]/option[4]'
        )

        driver.execute_script("arguments[0].value = '2500';", radius)
        log.info(f"{radius} Clicked with SUCCESS")
        search_field = driver.find_element_by_xpath(
            '//*[@id="StoreLocatorForm_Location"]'
        )
        xpath_search_button = '//*[@id="StoreLocatorForm_Submit"]'
        time.sleep(5)
        log.info("Sleeping until the search button visible")
        search_button = driver.find_element_by_xpath(xpath_search_button)
        search_field.clear()
        search_field.send_keys("NY")
        search_button.click()
        log.info("Search Button Clicked with SUCCESS")
        time.sleep(10)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        loclist = soup.find(
            "div",
            {
                "class": "StoreLocatorSidebarResultsLists StoreLocatorSidebarResultsListsActive"
            },
        ).findAll("ul")
        for loc in loclist:
            address = (
                loc.findAll("li")[2].get_text(separator="|", strip=True).split("|")
            )
            loc = loc["data-store"]
            loc = json.loads(loc)
            store_number = loc["ID"]
            location_name = loc["Name"]
            phone = loc["Phone"]
            page_url = "https://valuhomecenters.com/store-locator"
            street_address = address[0]
            address = address[1].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            latitude = loc["Latitude"]
            longitude = loc["Longitude"]
            yield SgRecord(
                locator_domain="https://valuhomecenters.com/",
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code="US",
                store_number=store_number,
                phone=phone,
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
