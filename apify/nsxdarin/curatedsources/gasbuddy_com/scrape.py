from typing import Iterable, Tuple, Callable, List
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.pause_resume import CrawlStateSingleton
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, Grain_1_KM
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
import json
from sglogging import sglog
from bs4 import BeautifulSoup as bs


log = sglog.SgLogSetup().get_logger(logger_name="gasbuddy")
page_urls: List[str] = []
proxy_url = "http://groups-RESIDENTIAL,country-us:{}@proxy.apify.com:8000/"


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


class ExampleSearchIteration(SearchIteration):
    def __init__(self, http: SgRequests):
        self.__http = http  # noqa
        self.__state = CrawlStateSingleton.get_instance()  # noqa

    def do(
        self,
        coord: Tuple[float, float],  # noqa
        zipcode: str,
        current_country: str,  # noqa
        items_remaining: int,  # noqa
        found_location_at: Callable[[float, float], None],  # noqa
    ) -> Iterable[SgRecord]:  # noqa

        log.info(zipcode)
        breaker = 0
        while True:
            breaker = breaker + 1
            if breaker == 10:
                raise Exception
            try:
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
                    "variables": {"fuel": 1, "maxAge": 0, "search": zipcode},
                    "operationName": "LocationBySearchTerm",
                }

                response = http.post(url, headers=headers, json=data).json()
                break
            except Exception:
                http.set_proxy_url(proxy_url)
                continue

        try:
            response["data"]["locationBySearchTerm"]["stations"]["results"]

        except Exception:
            return

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

            hmm = 0
            while True:
                hmm = hmm + 1
                if hmm == 100:
                    raise Exception
                try:
                    page_stuff = http.get(
                        page_url, headers={"User-Agent": "PostmanRuntime/7.19.0"}
                    )

                    if page_stuff.status_code != 404:
                        page_response = page_stuff.text
                        break

                    else:
                        break
                except Exception:
                    http.set_proxy_url(proxy_url)
                    continue

            if page_stuff.status_code == 404:
                phone = "<MISSING>"
                latitude = "<MISSING>"
                longitude = "<MISSING>"
                hours = "<MISSING>"

            else:
                page_soup = bs(page_response, "html.parser")
                page_soup.find("img")
                if (
                    '{"message":"Cannot return null for non-nullable field StationHours.status."}'
                    in page_response
                ):
                    phone = "<MISSING>"
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
                    hours = "<MISSING>"
                    yield SgRecord(
                        raw={
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
                    )
                    continue

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
                except Exception:
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

            yield SgRecord(
                raw={
                    "locator_domain": locator_domain,
                    "PAGE_URL": page_url,
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
            )


if __name__ == "__main__":
    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch", granularity=Grain_1_KM()
    )

    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=100
        )
    ) as writer:
        with SgRequests(dont_retry_status_codes=[403, 429, 500, 502, 404]) as http:
            search_iter = ExampleSearchIteration(http=http)
            par_search = ParallelDynamicSearch(
                search_maker=search_maker,
                search_iteration=search_iter,
                country_codes=[
                    SearchableCountries.USA,
                    SearchableCountries.CANADA,
                ],
            )

            for rec in par_search.run():
                writer.write_row(rec)

    state = CrawlStateSingleton.get_instance()
