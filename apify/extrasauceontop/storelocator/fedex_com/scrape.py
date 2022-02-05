from sgrequests import SgRequests
from sgscrape import simple_scraper_pipeline as sp
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_4


def get_data():
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        granularity=Grain_4(),
    )

    session = SgRequests()
    headers = {"accept": "application/json"}
    visited = []

    for search_lat, search_lon in search:
        url = (
            "https://local.fedex.com/en/search?q="
            + str(search_lat)
            + "%2C"
            + str(search_lon)
            + "&qp="
            + str(search_lat)
            + "%2C"
            + str(search_lon)
            + "&staffed=on&fdxType=5644121&fdxType=5644112&fdxType=5644117&fdxType=5644122&fdxType=5644123&fdxType=5644127&l=en"
        )
        response = session.get(url, headers=headers).json()

        for location in response["response"]["entities"]:
            locator_domain = "local.fedex.com"

            if location["url"] != "":
                page_url = "https://local.fedex.com/" + location["url"]
            else:
                page_url = "<MISSING>"

            location_name = location["profile"]["name"]

            try:
                latitude = location["profile"]["geocodedCoordinate"]["lat"]
                longitude = location["profile"]["geocodedCoordinate"]["long"]
            except Exception:
                try:
                    latitude = location["profile"]["displayCoordinate"]["lat"]
                    longitude = location["profile"]["displayCoordinate"]["long"]
                except Exception:
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"

            city = location["profile"]["address"]["city"]
            store_number = location["profile"]["meta"]["id"]
            address = (
                (
                    location["profile"]["address"]["line1"]
                    + " "
                    + str(location["profile"]["address"]["line2"])
                    + " "
                    + str(location["profile"]["address"]["line3"])
                )
                .replace("None", "")
                .strip()
            )
            state = location["profile"]["address"]["region"]
            zipp = location["profile"]["address"]["postalCode"]

            try:
                phone = location["profile"]["mainPhone"]["number"].replace("+", "")
            except Exception:
                phone = "<MISSING>"

            location_type = location["profile"]["name"]
            country_code = location["profile"]["address"]["countryCode"]

            try:
                hours = ""
                for hours_day in location["profile"]["hours"]["normalHours"]:
                    day = hours_day["day"]
                    try:
                        start = str(hours_day["intervals"][0]["start"])
                        end = str(hours_day["intervals"][0]["end"])
                    except Exception:
                        hours = hours + day + " " + "closed"
                    if start == "0":
                        start = "0:00"
                    else:
                        start = start[:-2] + ":" + start[-2:]

                    if end == "0":
                        end = "0:00"
                    else:
                        end = end[:-2] + ":" + end[-2:]

                    hours = hours + day + " " + start + "-" + end + ", "

                hours = hours[:-2]

            except Exception:
                hours = "<MISSING>"

            try:
                search.found_location_at(latitude, longitude)
            except Exception:
                pass

            if country_code != "US":
                continue

            if (
                location_name == "FedEx Office Print & Ship Center - Closed"
                or location_name == "FedEx Drop Box"
            ):
                continue

            location_data = [location_name, latitude, longitude]
            if location_data in visited:
                continue
            else:
                visited.append(location_data)
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
