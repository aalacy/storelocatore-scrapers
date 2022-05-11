import re
from sgzip.dynamic import SearchableCountries, DynamicZipSearch
from concurrent.futures import ThreadPoolExecutor, as_completed
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sglogging import sglog

logger = sglog.SgLogSetup().get_logger(logger_name="vw.com")


def write_output(data):
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        for row in data:
            writer.write_row(row)


def fetch_locations(postal, session):
    if len(postal) == 4:
        postal = "0" + postal
    url = f"https://www.vw.com/vwsdl/rest/product/dealers/zip/{postal}.json"
    logger.info(f"Crawling {url}")
    response = session.get(url)
    logger.info(f"Response: {response}")
    try:
        data = response.json()
        dealers = data.get("dealers", [])

        pois = []
        for dealer in dealers:
            # Page Url
            page_url = dealer["url"]

            # Store ID
            store_number = dealer["dealerid"]

            # Name
            location_name = dealer["name"]

            # Street
            street_address = (dealer["address1"] + " " + dealer["address2"]).strip()

            # Country
            country = dealer["country"]

            # State
            state = dealer["state"]

            # city
            city = dealer["city"]

            # zip
            postal = dealer["postalcode"]

            # Lat
            latitude = dealer["latlong"].split(",")[0]

            # Long
            longitude = dealer["latlong"].split(",")[1]

            # Phone
            phone = dealer["phone"]

            # hour
            regex = re.compile("sale", re.IGNORECASE)
            department_hours = dealer["hours"]
            department = next(
                (x for x in department_hours if regex.match(x.get("departmentName"))),
                None,
            )

            if not department:
                department = next(
                    (x for x in department_hours if x["departmentHours"]), None
                )

            hours_of_operation = (
                department.get("departmentHours", "<MISSING>")
                if department
                else "<MISSING>"
            )

            if isinstance(hours_of_operation, list):
                hours = []
                for day in hours_of_operation:
                    day_text = day["dayText"]

                    if day["isClosed"] == "Y":
                        hours.append(f"{day_text}: Closed")
                    else:
                        hours.append(
                            f'{day_text}: {day["openHour"]}-{day["closeHour"]}'
                        )

                hours_of_operation = ", ".join(hours)

            pois.append(
                SgRecord(
                    locator_domain="vw.com",
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=postal,
                    country_code=country,
                    store_number=store_number,
                    phone=phone,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )
            )

        return pois

    except Exception as e:
        logger.info(f"Error: {e}")
        pass


def fetch_data():
    with SgRequests() as session, ThreadPoolExecutor() as executor:
        search = DynamicZipSearch(
            country_codes=[SearchableCountries.USA], expected_search_radius_miles=50
        )
        futures = [
            executor.submit(fetch_locations, postal, session) for postal in search
        ]
        for future in as_completed(futures):
            for poi in future.result():
                yield poi


if __name__ == "__main__":
    data = fetch_data()
    write_output(data)
