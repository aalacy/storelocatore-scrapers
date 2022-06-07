# -*- coding: utf-8 -*-
import json
import undetected_chromedriver.v2 as uc
from sglogging import sglog
from selenium_stealth import stealth
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from webdriver_manager.chrome import ChromeDriverManager

website = "easyfinancial.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetch_data():

    options = uc.ChromeOptions()
    options.headless = True
    options.add_argument("--headless")
    with uc.Chrome(
        options=options, driver_executable_path=ChromeDriverManager().install()
    ) as session:
        stealth(
            session,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
        session.get("https://easyfinancial.com")

        payload = {
            "operationName": "getAllBranches",
            "variables": {"lat": 43.65413, "lng": -79.39242, "radius": 50000},
            "query": "query getAllBranches($lat: Float, $lng: Float, $radius: Float) { getAllBranches(lat: $lat, lng: $lng, radius: $radius) }",
        }

        result = session.execute_async_script(
            f"""
        fetch("https://be.easyfinancial.com/api/src?code=WLcdq2dRebMBytNYRbk7l/FOdQ8zAMXsKacLZV3vSqOJzknemwL9PQ==", {{
            "headers": {{
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9",
                "content-type": "application/json",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site"
            }},
            "referrer": "https://www.easyfinancial.com/",
            "referrerPolicy": "origin-when-cross-origin",
            "body": '{json.dumps(payload)}',
            "method": "POST",
            "mode": "cors",
            "credentials": "omit"
            }}).then(res => res.json()).then(arguments[0]);
        """
        )

        stores = result["data"]["getAllBranches"]

        for store in stores:
            page_url = "https://www.easyfinancial.com/find-branch"
            locator_domain = website
            location_name = store["storeNameC"]
            street_address = store["addressC"]
            if store["address2C"] is not None and len(store["address2C"]) > 0:
                street_address = street_address + ", " + store["address2C"]

            city = store["cityC"]
            state = store["provinceStateC"]
            if "-" in state:
                state = state.split("-")[0].strip()

            zip = store["postalCodeC"]

            country_code = store["countryC"]

            store_number = store["storeCodeC"]
            phone = store["storePhoneC"]

            location_type = store["typeC"]

            hours_list = []
            try:
                temp_hours = (
                    "Mon-Fri:"
                    + store["weekdayOpenC"][:2]
                    + ":"
                    + store["weekdayOpenC"][2:]
                    + "-"
                    + store["weekdayCloseC"][:2]
                    + ":"
                    + store["weekdayCloseC"][2:]
                )
                hours_list.append(temp_hours)
            except:
                pass

            try:
                temp_hours = (
                    "Sat:"
                    + store["saturdayOpenC"][:2]
                    + ":"
                    + store["saturdayOpenC"][2:]
                    + "-"
                    + store["saturdayCloseC"][:2]
                    + ":"
                    + store["saturdayCloseC"][2:]
                )
                hours_list.append(temp_hours)
            except:
                pass

            try:
                temp_hours = (
                    "Sun:"
                    + store["sundayOpenC"][:2]
                    + ":"
                    + store["sundayOpenC"][2:]
                    + "-"
                    + store["sundayCloseC"][:2]
                    + ":"
                    + store["sundayCloseC"][2:]
                )
                hours_list.append(temp_hours)
            except:
                pass

            hours_of_operation = "; ".join(hours_list).strip()

            latitude = str(store["lat"])
            longitude = str(store["lng"])

            yield SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
