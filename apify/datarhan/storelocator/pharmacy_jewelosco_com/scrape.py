# -*- coding: utf-8 -*-
import ssl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.static import static_coordinate_list, SearchableCountries
from sgselenium.sgselenium import SgFirefox

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

token = None


def fetch_token(driver):
    global token
    result = driver.execute_async_script(
        """
        var done = arguments[0]
        fetch("https://pharmacy.jewelosco.com/joweb/appload.htm", {
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            },
            "body": "formParams=null",
            "method": "POST",
        })
        .then(res => res.json())
        .then(done)
        .catch(done)
    """
    )

    token = result["token"][0]


def fetch_locations(coord, driver):
    try:
        lat, lng = coord
        result = driver.execute_async_script(
            f"""
            var done = arguments[0]
            fetch("https://pharmacy.jewelosco.com/joweb/getStoreList.htm", {{
                "headers": {{
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "csrfPreventionSalt": "{token}",
                }},
                "body": "formParams={{storeData: null,lat:{lat},lng:{lng},loggedIn:0}}",
                "method": "POST",
            }})
            .then(res => res.json())
            .then(done)
            .catch(done)
        """
        )

        if not result.get("data"):
            return []

        return result["data"]["stores"]["stores_list"]

    except Exception:
        fetch_token(driver)
        return fetch_locations(coord, driver)


def fetch_location(store_number, driver):
    try:
        result = driver.execute_async_script(
            f"""
            var done = arguments[0]
            fetch("https://pharmacy.jewelosco.com/joweb/getStoreDetails.htm", {{
                "headers": {{
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "csrfPreventionSalt": "{token}",
                }},
                "body": "formParams=%7B%22store_id%22%3A%22{store_number}%22%2C%22isLogged%22%3A%220%22%7D",
                "method": "POST",
            }})
            .then(res => res.json())
            .then(done)
            .catch(done)
        """
        )

        return result["data"]["stores"]
    except:
        fetch_token(driver)
        return fetch_location(store_number, driver)


def fetch_data():
    start_url = "https://pharmacy.jewelosco.com/joweb/#/store"
    domain = "pharmacy.jewelosco.com"

    all_coords = static_coordinate_list(10, SearchableCountries.USA)

    with SgFirefox(is_headless=True) as driver:
        driver.set_script_timeout(30)
        driver.get(start_url)
        fetch_token(driver)
        for code in all_coords:
            locations = fetch_locations(code, driver)

            for location in locations:
                store_number = location["id"]
                page_url = f"https://pharmacy.jewelosco.com/joweb/#/store/details/{store_number}"
                details = fetch_location(store_number, driver)

                location_name = details["store_name"]
                street_adddress = details["addressline1"]
                city = details["city"]
                state = details["state"]
                postal = details["zip"]
                phone = details["phone"]

                latitude = details["latitude"]
                longitude = details["longitude"]

                hours_of_operation = ",".join(
                    f'{day_hours["day"]}: {day_hours["hours"]}'
                    for day_hours in details["hours"]
                )

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_adddress,
                    city=city,
                    state=state,
                    zip_postal=postal,
                    country_code=SearchableCountries.USA,
                    store_number=store_number,
                    phone=phone,
                    location_type="",
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )

                yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
