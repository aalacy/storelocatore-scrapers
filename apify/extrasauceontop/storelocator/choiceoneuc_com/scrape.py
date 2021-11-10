from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import cloudscraper
import json
from sgscrape import simple_scraper_pipeline as sp


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
                    json_objects.append(json.loads(html_string[start : end + 1]))
                except Exception:
                    pass
        count = count + 1

    return json_objects


def get_data():

    session = SgRequests()

    scraper = cloudscraper.create_scraper(sess=session)

    url = "https://www.umms.org/health-services/urgent-care/locations"
    response = scraper.get(url).text

    soup = bs(response, "html.parser")

    loc_urls = [
        "https://www.umms.org" + a_tag["href"]
        for a_tag in soup.find(
            "ul", attrs={"class": "nav-content__nested-level"}
        ).find_all("a")
    ]

    for url in loc_urls:
        if (
            url
            == "https://www.umms.org/health-services/urgent-care/locations/telemedicine"
        ):
            continue
        response = scraper.get(url).text
        soup = bs(response, "html.parser")

        locator_domain = "www.umms.org"
        page_url = url

        json_objects = extract_json(response)
        location_name = soup.find(
            "h1", attrs={"class": "l-content-header__h1"}
        ).text.strip()
        address = json_objects[1]["items"][0]["address1"]
        city = json_objects[1]["items"][0]["address2"].split(",")[0]
        state = json_objects[1]["items"][0]["address2"].split(", ")[1].split(" ")[0]
        zipp = json_objects[1]["items"][0]["address2"].split(", ")[1].split(" ")[1][:5]
        country_code = "US"
        store_number = "<MISSING>"
        phone = json_objects[1]["items"][0]["phone"]
        location_type = "<MISSING>"
        latitude = json_objects[1]["items"][0]["coordinates"][0]["lat"]
        longitude = json_objects[1]["items"][0]["coordinates"][0]["lng"]

        hours = "Sun-Sat 8 am-8 pm"

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
