from sgrequests import SgRequests
from sgscrape import simple_scraper_pipeline as sp
from bs4 import BeautifulSoup as bs
from sgzip.dynamic import DynamicZipSearch, SearchableCountries, Grain_4
from sglogging import sglog


def get_data():
    log = sglog.SgLogSetup().get_logger(logger_name="walgreens")
    session = SgRequests()
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], granularity=Grain_4()
    )

    for search_code in search:
        if len(str(search_code)) == 4:
            search_code = "0" + str(search_code)
        params = {
            "requestType": "dotcom",
            "s": "1000",
            "p": "1",
            "zip": str(search_code),
        }

        url = "https://www.walgreens.com/locator/v1/stores/search?requestor=search"
        response = session.post(url, data=params).json()
        try:
            response["results"]
        except Exception:
            continue

        for location in response["results"]:
            locator_domain = "https://www.walgreens.com"
            page_url = locator_domain + location["storeSeoUrl"]
            location_name = location["store"]["address"]["street"]
            latitude = location["latitude"]
            longitude = location["longitude"]
            search.found_location_at(latitude, longitude)
            city = location["store"]["address"]["city"]
            store_number = location["storeNumber"]
            address = location_name
            state = location["store"]["address"]["state"]
            zipp = location["store"]["address"]["zip"]
            phone = location["store"]["phone"]["number"]
            location_type = "<MISSING>"
            country_code = "US"

            y = 0
            pharm_closed = "no"
            while True:
                y = y + 1
                if y == 10:
                    log.info(search_code)
                    log.info(location_name)
                    log.info(page_url)
                    raise Exception
                try:
                    hours_response = session.get(page_url).text
                    hours_soup = bs(hours_response, "html.parser")
                    if (
                        "The Pharmacy at this location is currently closed"
                        in hours_response
                    ):
                        pharm_closed = "yes"
                        break
                    pharmacy_check = hours_soup.find_all(
                        "li", attrs={"class": "accordion__drawer"}
                    )
                    x = 0
                    pharm_found = "no"
                    for pharm in pharmacy_check:
                        if "Pharmacy" in pharm.find("h2").text.strip():
                            pharm_found = "yes"
                            break
                        x = x + 1

                    if pharm_found == "yes":
                        hours_parts = (
                            pharmacy_check[x]
                            .find("li", attrs={"class": "single-hours-lists"})
                            .find_all("ul")
                        )

                    else:
                        hours_parts = (
                            pharmacy_check[0]
                            .find("li", attrs={"class": "single-hours-lists"})
                            .find_all("ul")
                        )

                    hours = ""
                    for part in hours_parts:
                        day = part.find("li", attrs={"class": "day"}).text.strip()
                        time = part.find("li", attrs={"class": "time"}).text.strip()

                        hours = hours + day + " " + time + ", "

                    hours = hours[:-2]
                    break
                except Exception:

                    try:
                        hours = "<MISSING>"
                        if "temporarily closed" in hours_response.lower():
                            hours = "nope"
                            break

                        else:
                            log.info(search_code)
                            log.info(location_name)
                    except Exception as e:
                        log.info(e)

            if hours == "nope":
                continue

            try:
                location["store"]["pharmacyOpenTime"]

            except Exception:
                continue

            if pharm_closed == "yes":
                continue

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


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"]),
        page_url=sp.MappingField(mapping=["page_url"], part_of_record_identity=True),
        location_name=sp.MappingField(
            mapping=["location_name"], part_of_record_identity=True
        ),
        latitude=sp.MappingField(mapping=["latitude"], part_of_record_identity=True),
        longitude=sp.MappingField(mapping=["longitude"], part_of_record_identity=True),
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
