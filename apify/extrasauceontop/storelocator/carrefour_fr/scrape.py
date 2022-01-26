from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
from sgscrape import simple_scraper_pipeline as sp
import os
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


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

                if "stores" in html_string[start : end + 1]:
                    try:
                        json_objects.append(json.loads(html_string[start : end + 1]))
                    except Exception:
                        pass
        count = count + 1

    return json_objects


def reset_sessions(data_url):
    s = SgRequests()

    driver = SgChrome(
        executable_path=ChromeDriverManager().install(), is_headless=True
    ).driver()
    driver.get(data_url)

    for request in driver.requests:

        headers = request.headers
        try:
            response = s.get(data_url, headers=headers)
            response_text = response.text

            test_html = response_text.split("div")
            if len(test_html) < 2:
                continue
            else:
                driver.quit()
                return [s, headers, response_text]

        except Exception:
            driver.quit()
            continue


def get_data():
    url = "https://www.carrefour.fr/magasin"

    response_stuff = reset_sessions(url)
    response = response_stuff[2]

    soup = bs(response, "html.parser")

    region_urls = [
        "https://www.carrefour.fr" + li_tag.find("a")["href"]
        for li_tag in soup.find_all(
            "li", attrs={"class": "store-locator-footer-list__item"}
        )
    ]

    for url in region_urls:
        response_session = reset_sessions(url)
        response = response_session[2]
        session = response_session[0]
        headers = response_session[1]
        json_objects = extract_json(response)

        for location in json_objects[1]["search"]["data"]["stores"]:
            locator_domain = "carrefour.fr"

            page_url = "https://www.carrefour.fr" + location["storePageUrl"]
            location_name = location["name"]
            latitude = location["address"]["geoCoordinates"]["latitude"]
            longitude = location["address"]["geoCoordinates"]["latitude"]
            city = location["address"]["city"]
            store_number = location["id"]
            address = (
                location["address"]["address1"]
                + " "
                + location["address"]["address2"]
                + " "
                + location["address"]["address3"]
            ).strip()

            if address[-1] == "0":
                address = address[:-2]

            state = location["address"]["region"]
            zipp = location["address"]["postalCode"]

            try:
                phone_response = session.get(page_url, headers=headers).text

            except Exception:
                response_session = reset_sessions(url)
                phone_response = response_session[2]
                session = response_session[0]
                headers = response_session[1]

            phone_soup = bs(phone_response, "html.parser")
            a_tags = phone_soup.find_all("a")

            phone = "<MISSING>"
            for a_tag in a_tags:
                if "tel:" in a_tag["href"]:
                    phone = a_tag["href"].replace("tel:", "")
                    break

            location_type = "<MISSING>"
            country_code = location["address"]["countryCode"]

            if page_url != "https://www.carrefour.fr/magasin/":
                hours_parts = phone_soup.find_all(
                    "div", attrs={"class": "store-meta__opening-range"}
                )
                hours = ""
                for part in hours_parts:
                    day = part.find(
                        "div", attrs={"class": "store-meta__label"}
                    ).text.strip()
                    times = part.find_all(
                        "div", attrs={"class": "store-meta__time-range"}
                    )

                    time_part = ""
                    for time in times:
                        time_part = time_part + time.text.strip() + " "

                    time_part = time_part.strip()

                    hours = hours + day + " " + time_part + ", "

                hours = hours[:-2]
                hours = hours.replace("à", "-")

            else:
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


def scrape():

    try:
        proxy_pass = os.environ["PROXY_PASSWORD"]

    except Exception:
        proxy_pass = "No"

    if proxy_pass == "No":
        raise Exception("Run this with a proxy")

    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"]),
        page_url=sp.MappingField(mapping=["page_url"], part_of_record_identity=True),
        location_name=sp.MappingField(
            mapping=["location_name"], part_of_record_identity=True
        ),
        latitude=sp.MappingField(mapping=["latitude"], is_required=False),
        longitude=sp.MappingField(mapping=["longitude"], is_required=False),
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
