import json
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgzip.dynamic import DynamicZipSearch, SearchableCountries, Grain_4
from sgscrape import simple_scraper_pipeline as sp
import html


def extract_json(html_string):
    html_string = (
        html_string.replace("\n", "")
        .replace("\r", "")
        .replace("\t", "")
        .replace(" /* forcing open state for all FCs*/", "")
    )
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
                    json_objects.append(json.loads(html_string[start : end + 1]))
                except Exception:
                    pass
        count = count + 1

    return json_objects


def get_data():
    page_urls = []
    with SgRequests(verify_ssl=False) as session:
        search = DynamicZipSearch(
            country_codes=[SearchableCountries.USA],
            granularity=Grain_4(),
            max_search_results=25,
        )

        for search_code in search:
            url = (
                "https://www.regions.com/Locator?regions-get-directions-starting-coords=&daddr=&autocompleteAddLat=&autocompleteAddLng=&r=&geoLocation="
                + search_code
                + "&type=branch"
            )

            response_stuff = session.get(url)
            response = response_stuff.text
            soup = bs(response, "html.parser")
            grids = soup.find_all("li", attrs={"class": "locator-result__list-item"})

            for grid in grids:
                locator_domain = "regions.com"

                a_tag = grid.find("a")
                try:
                    page_url = ("https://regions.com" + a_tag["href"]).lower()
                except Exception:
                    page_url = "<MISSING>"

                if page_url != "<MISSING>":
                    page_response = session.get(page_url).text
                    page_soup = bs(page_response, "html.parser")

                    json_objects = extract_json(
                        page_response.split("application/ld+json")[1]
                    )[0]

                    if (
                        "-atm-" not in page_url
                        and "ATM Location and Features" not in page_response
                    ):
                        continue

                    location_name = json_objects["name"]
                    latitude = json_objects["geo"]["latitude"]
                    longitude = json_objects["geo"]["longitude"]
                    search.found_location_at(latitude, longitude)
                    address = json_objects["address"]["streetAddress"]
                    store_number = page_response.split("directionId=")[1].split("&")[0]
                    city = json_objects["address"]["addressLocality"]
                    state = json_objects["address"]["addressRegion"]
                    zipp = json_objects["address"]["postalCode"]

                    phone_checks = page_soup.find_all("a", attrs={"class": "rds-link"})
                    for phone_check in phone_checks:
                        if "tel:" in phone_check["href"]:
                            phone = (
                                phone_check["href"].replace("tel:", "").replace("+", "")
                            )
                            break

                    location_type = "ATM"

                    try:
                        lis = page_soup.find_all("li")
                        for li in lis:
                            if "ATM Hours" in li.text.strip():
                                hours = li.text.strip().replace("ATM Hours: ", "")
                    except Exception:
                        hours = "<MISSING>"

                    country_code = zipp = json_objects["address"]["addressCountry"][
                        "name"
                    ]

                    yield {
                        "locator_domain": html.unescape(locator_domain),
                        "page_url": html.unescape(page_url),
                        "location_name": html.unescape(location_name),
                        "latitude": latitude,
                        "longitude": longitude,
                        "city": html.unescape(city),
                        "store_number": store_number,
                        "street_address": html.unescape(address),
                        "state": html.unescape(state),
                        "zip": html.unescape(zipp),
                        "phone": phone,
                        "location_type": html.unescape(location_type),
                        "hours": html.unescape(hours),
                        "country_code": country_code,
                    }


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
