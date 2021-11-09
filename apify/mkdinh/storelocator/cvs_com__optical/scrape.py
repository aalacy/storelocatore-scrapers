import re
import json
import threading

from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("cvs_com")


thread_local = threading.local()
base_url = "https://www.cvs.com"

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
}


def write_output(data):
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=20000
        )
    ) as writer:
        for row in data:
            writer.write_row(row)


def get_session():
    if (
        not hasattr(thread_local, "session")
        or thread_local.request_count > 10
        or thread_local.session_failed
    ):
        thread_local.session = SgRequests()
        thread_local.request_count = 0
        thread_local.session_failed = False

    thread_local.request_count += 1
    return thread_local.session


def fetch_locations(coord):
    locations = []
    session = get_session()

    headers = {
        "x-api-key": "k6DnPo1puMOQmAhSCiRGYvzMYOSFu903",
    }

    params = {
        "latitude": coord[0],
        "longitude": coord[1],
        "searchText": "",
        "filters": "",
        "resultCount": 25,
        "pageNum": 1,
    }

    try:
        response = session.get(
            "https://api.cvshealth.com/locator/v1/stores/search",
            headers=headers,
            params=params,
        )
        data = response.json()
    except:
        logger.error(f"fail to fetch: {coord}")
        return locations

    stores = data.get("storeList", [])

    for store in stores:
        locator_domain = "cvs.com"
        info = store["storeInfo"]

        store_number = info.get("storeId")
        latitude = info.get("latitude")
        longitude = info.get("longitude")
        phone = info.get("phoneNumbers", [])[0]["retail"]

        address = store["address"]
        street_address = address.get("street")
        city = address.get("city")
        state = address.get("state")
        zip_postal = address.get("zip")
        country_code = "US"

        hours_of_operation = get_hours_of_operation(store)

        location_name = f"CVS Pharmacy at {street_address} {city}, {state} {zip_postal}"

        page_url = f'https://www.cvs.com/store-locator/{re.sub(" ", "-", city).lower()}-{state.lower()}-pharmacies/store-details/storeid={store_number}'
        location_type = "Healthhub_Ind"

        locations.append(
            SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                location_type=location_type,
                store_number=store_number,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                hours_of_operation=hours_of_operation,
            )
        )

    return locations


def get_hours_of_operation(store):
    departments = store.get("hours")["departments"]
    for department in departments:
        days = department.get("regHours")
        if department["regHours"]:
            return ", ".join(
                f'{day["weekday"]}: {day["startTime"]}-{day["endTime"]}' for day in days
            )


def fetch_location(page_url, session):
    response = session.get(page_url)
    soup = BeautifulSoup(response.text)
    locator_domain = "cvs.com"

    try:
        details = soup.find("cvs-store-details")["sd-props"]
        data = json.loads(details)
        general = data["cvsMyStoreDetailsProps"]["store"]

        store_number = general["storeId"]
        phone = general["phoneNumber"]
        location_type = "Optical"
        location_name = data["cvsLocationGeneralDetailsProps"]["storeAddress"][
            "firstLine"
        ]

        street_address = general["street"]
        city = general["city"]
        state = general["state"]
        zip_postal = general["zip"]
        country_code = "US"
        latitude = general["latitude"]
        longitude = general["longitude"]

        hours = data["cvsLocationHoursProps"]["locationHours"][0]["hours"]

        hours_of_operation = []
        for hour in hours:
            day = hour["titleText"]
            try:
                start = hour["startTime"]
                end = hour["endTime"]
            except:
                start = "Closed"
                end = "Closed"

            if day != "Today":
                time = (
                    start
                    if start == "Open 24 Hours" or start == "Closed"
                    else f"{start}-{end}"
                )
                hours_of_operation.append(f"{day}: {time}")

        hours_of_operation = ", ".join(hours_of_operation)
    except:
        script = soup.find("script", type="application/ld+json")
        details = json.loads(script.string)

        store_number = details["@id"]
        phone = details["telephone"]
        location_type = "Optical"

        address = details["address"]
        street_address = address["streetAddress"]
        city = address["addressLocality"]
        state = address["addressRegion"]
        zip_postal = address["postalCode"]
        country_code = "US"

        geo = details["geo"]
        latitude = geo["latitude"]
        longitude = geo["longitude"]

        location_name = f"CVS Optical {city}"
        hours = details["openingHoursSpecification"]

        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        hours_of_operation = []
        for day in days:
            for hour in hours:
                day_of_week = hour["dayOfWeek"]
            try:
                opens = hour["opens"]
                closes = hour["closes"]
            except:
                opens = "Closed"
                closes = "Closed"

                if day == day_of_week:
                    time = opens if opens == "Closed" else f"{opens}: {closes}"
                    hours_of_operation.append(f"{day_of_week}: {time}")

        hours_of_operation = ", ".join(hours_of_operation)

    return SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=zip_postal,
        country_code=country_code,
        store_number=store_number,
        phone=phone,
        location_type=location_type,
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )


def scrape():
    with SgRequests() as session:
        response = session.get("https://www.cvs.com/optical/optical-center-locations")
        soup = BeautifulSoup(response.text)

        locations = soup.find_all("div", class_="location-city")
        for location in locations:
            url = location.find("a")["href"].strip()
            yield fetch_location(url, session)


if __name__ == "__main__":
    data = scrape()
    write_output(data)
