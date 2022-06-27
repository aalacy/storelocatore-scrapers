from sgrequests import SgRequests
from sgscrape import simple_scraper_pipeline as sp
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
import re


def get_data():
    search = DynamicZipSearch(country_codes=[SearchableCountries.CANADA])

    session = SgRequests()
    url = "https://on-api.mycarecompass.lifelabs.com/api/LocationFinder/GetLocations/"
    false = False

    for search_code in search:
        try:
            params = {
                "address": search_code,
                "locationCoordinate": {"latitude": 0, "longitude": 0},
                "locationFinderSearchFilters": {
                    "isOpenEarlySelected": false,
                    "isOpenWeekendsSelected": false,
                    "isOpenSundaysSelected": false,
                    "isWheelchairAccessibleSelected": false,
                    "isDoesECGSelected": false,
                    "isDoes24HourHolterMonitoringSelected": false,
                    "isDoesAmbulatoryBloodPressureMonitoringSelected": false,
                    "isDoesServeAutismSelected": false,
                    "isGetCheckedOnlineSelected": false,
                    "isOpenSaturdaysSelected": false,
                    "isCovid19TestingSiteSelected": false,
                },
            }
            response = session.post(url, json=params).json()

            for location in response["entity"]:
                locator_domain = "lifelabs.com"
                page_url = (
                    "https://www.on.mycarecompass.lifelabs.com/appointmentbooking?siteId="
                    + str(location["locationId"])
                )
                location_name = location["pscName"]
                address = location["locationAddress"]["street"]
                x = 0
                for character in address:
                    if bool(re.search(r"\d", character)) is True:
                        break

                    x = x + 1
                address = address[x:]
                city = location["locationAddress"]["city"]
                state = location["locationAddress"]["province"]
                zipp = location["locationAddress"]["postalCode"]
                country_code = "CA"
                store_number = location["locationId"]
                phone = location["phone"]
                location_type = "<MISSING>"
                latitude = location["locationCoordinate"]["latitude"]
                longitude = location["locationCoordinate"]["longitude"]
                search.found_location_at(latitude, longitude)

                hours = ""
                x = 0
                days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
                for part in location["hoursOfOperation"]:

                    try:
                        day = days[x]
                        start = part["openTime"]
                        end = part["closeTime"]
                        hours = hours + day + " " + start + "-" + end + ", "

                    except Exception:
                        day = days[x]
                        hours = hours + day + " " + "closed" + ", "
                    x = x + 1

                hours = hours[:-2]

                if (
                    hours
                    == "mon closed, tue closed, wed closed, thu closed, fri closed, sat closed, sun closed"
                ):
                    continue
                if zipp is None or zipp == "None":
                    zipp = "<MISSING>"
                yield {
                    "locator_domain": locator_domain,
                    "page_url": page_url,
                    "location_name": location_name,
                    "latitude": latitude,
                    "longitude": longitude,
                    "city": city,
                    "store_number": store_number,
                    "street_address": address,
                    "state": state,
                    "zip": zipp,
                    "phone": phone,
                    "location_type": location_type,
                    "hours": hours,
                    "country_code": country_code,
                }

        except Exception:
            continue


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"]),
        page_url=sp.MappingField(mapping=["page_url"], part_of_record_identity=True),
        location_name=sp.MappingField(
            mapping=["location_name"],
        ),
        latitude=sp.MappingField(
            mapping=["latitude"],
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
        ),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], is_required=False
        ),
        city=sp.MappingField(
            mapping=["city"],
        ),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MultiMappingField(mapping=["zip"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"]),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(
            mapping=["store_number"], part_of_record_identity=True
        ),
        hours_of_operation=sp.MappingField(mapping=["hours"], is_required=False),
        location_type=sp.MappingField(mapping=["location_type"], is_required=False),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=get_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )
    pipeline.run()


scrape()
