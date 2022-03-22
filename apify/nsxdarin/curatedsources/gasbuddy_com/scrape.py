from sgrequests import SgRequests
import json
from sgzip.dynamic import DynamicZipSearch, SearchableCountries, Grain_1_KM
from sgscrape import simple_scraper_pipeline as sp
from bs4 import BeautifulSoup as bs
from sglogging import sglog

log = sglog.SgLogSetup().get_logger(logger_name="gasbuddy")


def extract_json(html_string):
    json_objects = []
    count = 0

    brace_count = 0
    for element in html_string:

        if element == "{":
            brace_count = brace_count + 1
            if brace_count == 1:
                start = count

        elif element == "}":
            brace_count = brace_count - 1
            if brace_count == 0:
                end = count
                try:
                    if "latitude" in html_string[start : end + 1]:
                        json_objects.append(json.loads(html_string[start : end + 1]))
                except Exception:
                    pass
        count = count + 1

    return json_objects


def set_session(search_code):
    session = SgRequests(retries_with_fresh_proxy_ip=5)
    url = "https://www.gasbuddy.com/graphql"
    headers = {
        "User-Agent": "PostmanRuntime/7.19.0",
        "Upgrade-Insecure-Requests": "1",
        "DNT": "1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
    }
    data = {
        "query": "query LocationBySearchTerm($brandId: Int, $cursor: String, $fuel: Int, $lat: Float, $lng: Float, $maxAge: Int, $search: String) {\n  locationBySearchTerm(lat: $lat, lng: $lng, search: $search) {\n    countryCode\n    displayName\n    latitude\n    longitude\n    regionCode\n    stations(brandId: $brandId, cursor: $cursor, fuel: $fuel, maxAge: $maxAge) {\n      count\n      cursor {\n        next\n        __typename\n      }\n      results {\n        address {\n          country\n          line_1\n          line_2\n          locality\n          postal_code\n          region\n          __typename\n        }\n        badges {\n          badgeId\n          callToAction\n          campaignId\n          clickTrackingUrl\n          description\n          detailsImageUrl\n          detailsImpressionTrackingUrls\n          imageUrl\n          impressionTrackingUrls\n          targetUrl\n          title\n          __typename\n        }\n        brandings {\n          brand_id\n          branding_type\n          __typename\n        }\n        brands {\n          brand_id\n          image_url\n          name\n          __typename\n        }\n        emergency_status {\n          has_diesel {\n            nick_name\n            report_status\n            update_date\n            __typename\n          }\n          has_gas {\n            nick_name\n            report_status\n            update_date\n            __typename\n          }\n          has_power {\n            nick_name\n            report_status\n            update_date\n            __typename\n          }\n          __typename\n        }\n        enterprise\n        fuels\n        id\n        name\n        offers {\n          discounts {\n            grades\n            pwgb_discount\n            __typename\n          }\n          types\n          __typename\n        }\n        pay_status {\n          is_pay_available\n          __typename\n        }\n        prices {\n          cash {\n            nickname\n            posted_time\n            price\n            __typename\n          }\n          credit {\n            nickname\n            posted_time\n            price\n            __typename\n          }\n          discount\n          fuel_product\n          __typename\n        }\n        ratings_count\n        star_rating\n        __typename\n      }\n      __typename\n    }\n    trends {\n      areaName\n      today\n      todayLow\n      trend\n      __typename\n    }\n    __typename\n  }\n}\n",
        "variables": {"fuel": 1, "maxAge": 0, "search": search_code},
        "operationName": "LocationBySearchTerm",
    }

    response = session.post(url, headers=headers, json=data).json()

    return [session, headers, response]


def set_get_session(page_url):
    x = 0
    while True:
        x = x + 1
        if x == 100:
            raise Exception
        try:
            session = SgRequests(retries_with_fresh_proxy_ip=5)
            page_response = session.get(
                page_url, headers={"User-Agent": "PostmanRuntime/7.19.0"}
            ).text
            break
        except Exception:
            continue

    return [session, page_response]


def get_data():
    url = "https://www.gasbuddy.com/graphql"
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
        granularity=Grain_1_KM(),
    )

    x = 0
    y = 0

    error_count = 0
    page_urls = []
    for search_code in search:
        log.info(search_code)
        x = x + 1
        if len(str(search_code)) == 4:
            search_code = "0" + str(search_code)

        if x == 1:
            response_stuff = set_session(search_code)
            session = response_stuff[0]
            headers = response_stuff[1]
            response = response_stuff[2]

        elif y == 400:
            y = 0
            response_stuff = set_session(search_code)
            session = response_stuff[0]
            headers = response_stuff[1]
            response = response_stuff[2]

        else:
            try:
                data = {
                    "query": "query LocationBySearchTerm($brandId: Int, $cursor: String, $fuel: Int, $lat: Float, $lng: Float, $maxAge: Int, $search: String) {\n  locationBySearchTerm(lat: $lat, lng: $lng, search: $search) {\n    countryCode\n    displayName\n    latitude\n    longitude\n    regionCode\n    stations(brandId: $brandId, cursor: $cursor, fuel: $fuel, maxAge: $maxAge) {\n      count\n      cursor {\n        next\n        __typename\n      }\n      results {\n        address {\n          country\n          line_1\n          line_2\n          locality\n          postal_code\n          region\n          __typename\n        }\n        badges {\n          badgeId\n          callToAction\n          campaignId\n          clickTrackingUrl\n          description\n          detailsImageUrl\n          detailsImpressionTrackingUrls\n          imageUrl\n          impressionTrackingUrls\n          targetUrl\n          title\n          __typename\n        }\n        brandings {\n          brand_id\n          branding_type\n          __typename\n        }\n        brands {\n          brand_id\n          image_url\n          name\n          __typename\n        }\n        emergency_status {\n          has_diesel {\n            nick_name\n            report_status\n            update_date\n            __typename\n          }\n          has_gas {\n            nick_name\n            report_status\n            update_date\n            __typename\n          }\n          has_power {\n            nick_name\n            report_status\n            update_date\n            __typename\n          }\n          __typename\n        }\n        enterprise\n        fuels\n        id\n        name\n        offers {\n          discounts {\n            grades\n            pwgb_discount\n            __typename\n          }\n          types\n          __typename\n        }\n        pay_status {\n          is_pay_available\n          __typename\n        }\n        prices {\n          cash {\n            nickname\n            posted_time\n            price\n            __typename\n          }\n          credit {\n            nickname\n            posted_time\n            price\n            __typename\n          }\n          discount\n          fuel_product\n          __typename\n        }\n        ratings_count\n        star_rating\n        __typename\n      }\n      __typename\n    }\n    trends {\n      areaName\n      today\n      todayLow\n      trend\n      __typename\n    }\n    __typename\n  }\n}\n",
                    "variables": {"fuel": 1, "maxAge": 0, "search": search_code},
                    "operationName": "LocationBySearchTerm",
                }

                response = session.post(url, headers=headers, json=data).json()
                if (
                    response["data"]["locationBySearchTerm"]["stations"]["results"]
                    is None
                ):
                    session_response = set_session(search_code)
                    session = session_response[0]
                    response = session_response[1]

            except Exception:
                breaker = 0
                while True:
                    breaker = breaker + 1
                    if breaker == 10:
                        log.info("We broke here")
                        raise Exception
                    try:
                        response_stuff = set_session(search_code)
                        session = response_stuff[0]
                        headers = response_stuff[1]
                        response = response_stuff[2]
                        break

                    except Exception:
                        continue

        try:
            response["data"]["locationBySearchTerm"]["stations"]["results"]

        except Exception:
            continue

        y = y + 1
        log.info("here")
        for location in response["data"]["locationBySearchTerm"]["stations"]["results"]:
            locator_domain = "gasbuddy.com"
            page_url = "https://www.gasbuddy.com/station/" + location["id"]
            if page_url in page_urls:
                continue

            page_urls.append(page_url)
            log.info(page_url)
            location_name = location["name"]

            city = location["address"]["locality"]
            store_number = location["id"]
            address = (
                location["address"]["line_1"] + " " + location["address"]["line_2"]
            ).strip()
            state = location["address"]["region"]
            zipp = location["address"]["postal_code"]
            location_type = "fuel_station"
            country_code = location["address"]["country"]

            if y == 0:
                page_stuff = set_get_session(page_url)
                session = page_stuff[0]
            try:
                page_status = session.get(
                    page_url, headers={"User-Agent": "PostmanRuntime/7.19.0"}
                )

                if page_status.status_code != 404:
                    page_response = page_status.text
                    page_soup = bs(page_response, "html.parser")
                    if (
                        '{"message":"Cannot return null for non-nullable field StationHours.status."}'
                        in page_response
                    ):
                        continue
                    page_soup.find("img")

                else:
                    page_response = "broken"

            except Exception:
                page_stuff = set_get_session(page_url)
                session = page_stuff[0]
                page_response = page_stuff[1]
                page_soup = bs(page_response, "html.parser")
                page_soup.find("img")

            if page_response != "broken":
                try:
                    phone = page_soup.find(
                        "a", attrs={"class": "StationInfoBox-module__phoneLink___2LtAk"}
                    ).text.strip()

                except Exception:
                    phone = "<MISSING>"
                json_objects = extract_json(page_response)

                try:
                    latitude = json_objects[-1]["@graph"][-1]["geo"]["latitude"]
                    longitude = json_objects[-1]["@graph"][-1]["geo"]["longitude"]
                    search.found_location_at(latitude, longitude)
                except Exception:
                    error_count = error_count + 1
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"

                hours = ""
                hours_parts = page_soup.find_all(
                    "span", attrs={"class": "StationHours-module__statusOpen___360-J"}
                )
                for part in hours_parts:
                    hours = hours + part.text.strip() + ", "

                hours = hours[:-2]

                if hours == "":
                    hours = "<MISSING>"

            else:
                phone = "<MISSING>"
                latitude = "<MISSING>"
                longitude = "<MISSING>"
                hours = "<MISSING>"

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

    log.info(error_count)


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
