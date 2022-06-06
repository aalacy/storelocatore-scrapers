import ssl
import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgselenium import SgFirefox
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from selenium.webdriver.common.by import By
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

ssl._create_default_https_context = ssl._create_unverified_context


DOMAIN = "therange.co.uk"
website = "https://www.therange.co.uk/"
store_locator = f"{website}stores/"
MISSING = SgRecord.MISSING
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def fetch_data():
    with SgFirefox() as driver:
        driver.get(store_locator)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        loclist = soup.find("ul", {"id": "storelist"}).findAll("li")
        for loc in loclist:
            page_url = "https://www.therange.co.uk" + loc.find("a")["href"]
            log.info(page_url)
            driver.get(page_url)
            response = driver.page_source
            temp = json.loads(
                response.split('<script type="application/ld+json">')[1].split(
                    "</script>"
                )[0]
            )
            location_name = temp["name"]
            phone = temp["telephone"]
            address = temp["address"]
            street_address = address["streetAddress"]
            city = address["addressLocality"]
            state = address["addressRegion"]
            zip_postal = address["postalCode"]
            country_code = address["addressCountry"]
            hour_list = temp["openingHoursSpecification"]
            hours_of_operation = ""
            for hour in hour_list:
                hours_of_operation = (
                    hours_of_operation
                    + " "
                    + hour["dayOfWeek"].replace("http://schema.org/", "")
                    + " "
                    + hour["opens"]
                    + "-"
                    + hour["closes"]
                )
            if "Closed-Closed" in hours_of_operation:
                continue
            try:
                geo_link = driver.find_element(
                    By.XPATH, '//div[@class="google-maps-link"]/a'
                ).get_attribute("href")

                log.info(f"GEO LINK: {geo_link}")
                latitude = geo_link.split("ll=")[1].split(",")[0].strip()
                longitude = geo_link.split("ll=")[1].split(",")[1].split("&")[0].strip()
            except:
                latitude = MISSING
                longitude = MISSING
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=MISSING,
                phone=phone,
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
