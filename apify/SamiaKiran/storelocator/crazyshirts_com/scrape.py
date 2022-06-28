import ssl
import json
from sglogging import sglog
from sgselenium import SgChrome
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


ssl._create_default_https_context = ssl._create_unverified_context

session = SgRequests()
website = "crazyshirts.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://www.crazyshirts.com"
MISSING = SgRecord.MISSING


def get_cookies(url):
    cookies = []
    with SgChrome() as driver:
        driver.get(url)
        for cookie in driver.get_cookies():
            cookies.append(f"{cookie['name']}={cookie['value']}")
            headers["cookie"] = "; ".join(cookies)


def fetch_data():
    if True:
        url = "https://www.crazyshirts.com/store-locator"
        get_cookies(url)
        api_url = "https://www.crazyshirts.com/api/commerce/storefront/locationUsageTypes/SP/locations/?startIndex=0&pageSize=1000&includeAttributeDefinition=true"
        r = session.get(api_url, headers=headers)
        loclist = json.loads(r.text)["items"]
        for loc in loclist:
            location_name = loc["name"]
            store_number = loc["code"]
            page_url = "https://www.crazyshirts.com/store-details?code=" + store_number
            log.info(page_url)
            phone = loc["phone"]
            address = loc["address"]
            try:
                street_address = address["address1"] + " " + address["address2"]
            except:
                street_address = address["address1"]
            street_address = street_address.replace(
                "Planet Hollywood Resort & Casino", ""
            )
            log.info(street_address)
            city = address["cityOrTown"]
            state = address["stateOrProvince"]
            zip_postal = address["postalOrZipCode"]
            country_code = address["countryCode"]
            latitude = loc["geo"]["lat"]
            longitude = loc["geo"]["lng"]
            day = loc["regularHours"]
            sun = " Sun" + day["sunday"]["label"]
            mon = "Mon " + day["monday"]["label"]
            tue = " Tue " + day["tuesday"]["label"]
            wed = " Wed " + day["wednesday"]["label"]
            thu = " Thu " + day["thursday"]["label"]
            fri = " Fri " + day["friday"]["label"]
            sat = " Sat " + day["saturday"]["label"]
            hours_of_operation = mon + tue + wed + thu + fri + sat + sun
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=store_number,
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
