from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp
import json


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
                    if "day" in html_string[start : end + 1]:
                        json_objects.append(json.loads(html_string[start : end + 1]))
                except Exception:
                    pass
        count = count + 1

    return json_objects


def get_data():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"
    }
    response = session.get("https://locations.modpizza.com/usa", headers=headers).text
    soup = bs(response, "html.parser")

    state_urls = [
        "https://locations.modpizza.com/" + a_tag["href"]
        for a_tag in soup.find_all("a", attrs={"class": "Directory-listLink"})
    ]

    page_urls = []
    city_urls = []
    for state_url in state_urls:
        page_url_check = state_url.split("/")[-1]
        if len(page_url_check) != 2:
            page_urls.append(state_url)
            continue

        state_response = session.get(state_url).text
        state_soup = bs(state_response, "html.parser")

        for a_tag in state_soup.find_all("a", attrs={"class": "Directory-listLink"}):
            city_urls.append(
                "https://locations.modpizza.com" + a_tag["href"].replace("..", "")
            )

    for city_url in city_urls:
        page_url_check = city_url.split("usa/")[1].split("/")
        if len(page_url_check) == 3:
            page_urls.append(city_url)
            continue

        city_response = session.get(city_url).text
        city_soup = bs(city_response, "html.parser")

        for a_tag in city_soup.find_all("a", attrs={"class": "Teaser-titleLink Link"}):
            page_urls.append(
                "https://locations.modpizza.com" + a_tag["href"].replace("..", "")
            )

    for page_url in page_urls:
        locator_domain = "modpizza.com"

        page_response = session.get(page_url).text
        soup = bs(page_response, "html.parser")

        location_name = soup.find(
            "span", attrs={"class": "Hero-geo Heading--lead"}
        ).text.strip()

        if "coming soon" in location_name.lower():
            continue

        lat_lon_parts = str(soup.find("script", attrs={"class": "js-map-data"}))
        latitude = lat_lon_parts.split(":")[1].split(",")[0]
        longitude = lat_lon_parts.split(",")[1].split(":")[1].split("}")[0]

        city = soup.find(
            "span", attrs={"class": "Address-field Address-city"}
        ).text.strip()
        address = soup.find(
            "span", attrs={"class": "Address-field Address-line1"}
        ).text.strip()

        try:
            address2 = soup.find(
                "span", attrs={"class": "Address-field Address-line2"}
            ).text.strip()
            address = address + " " + address2

        except Exception:
            pass
        state = page_url.split("/")[-3]
        zipp = soup.find(
            "span", attrs={"class": "Address-field Address-postalCode"}
        ).text.strip()

        try:
            phone = soup.find(
                "span", attrs={"class": "Text Phone-text Phone-number"}
            ).text.strip()
        except Exception:
            phone = "<MISSING>"

        location_type = "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"

        hours_parts = extract_json(page_response)[-1]["hours"]
        hours = ""
        if "1400 Hwy 17 N Unit 5" in address:
            hours_parts = extract_json(page_response)[14]["hours"]

        for part in hours_parts:
            day = part["day"]
            if len(part["intervals"]) == 0:
                continue
            start = (
                str(part["intervals"][0]["start"])[:-2]
                + ":"
                + str(part["intervals"][0]["start"])[-2:]
            )
            end = (
                str(part["intervals"][0]["end"])[:-2]
                + ":"
                + str(part["intervals"][0]["end"])[-2:]
            )

            hours = hours + day + " " + str(start) + "-" + str(end) + ", "

        hours = hours[:-2]

        address = address.split(" across")[0]
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
