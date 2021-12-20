from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import pandas as pd
from sgscrape import simple_scraper_pipeline as sp
import json


def extract_json(html_string):
    json_objects = []
    count = 0

    brace_count = 0
    for element in html_string:

        if element == "[":
            brace_count = brace_count + 1
            if brace_count == 1:
                start = count

        elif element == "]":
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
    response = session.get(
        "https://www.google.com/maps/d/kml?mid=1k_5K2ikpmcAyElx_ND0io5MT-3w&forcekml=1"
    ).text

    soup = bs(response, "html.parser")

    places = soup.find_all("placemark")

    latitudes = []
    longitudes = []

    page_urls = []
    locator_domains = []
    country_codes = []
    location_types = []
    names = []
    addresses = []
    citys = []
    states = []
    zips = []
    phones = []
    hours = []
    store_numbers = []

    for place in places:
        name = place.find("name").text.strip()
        page_url = place.find(attrs={"name": "URL"}).text.strip()
        street = place.find(attrs={"name": "Address"}).text.strip()
        city = place.find(attrs={"name": "City"}).text.strip()
        state = place.find(attrs={"name": "State"}).text.strip()
        zip_code = place.find(attrs={"name": "ZIP"}).text.strip()
        phone = place.find(attrs={"name": "Phone"}).text.strip()
        hour = place.find(attrs={"name": "Store Hrs."}).text.strip()

        # for some reason the 0 is trimmed off of zip codes beginning with 0. Add that back here
        if len(zip_code) == 4:
            zip_code = "0" + zip_code
        names.append(name)
        addresses.append(street)
        citys.append(city)
        states.append(state)
        zips.append(zip_code)
        phones.append(phone)
        hours.append(hour)
        page_urls.append(page_url)

        locator_domains.append("premierrents.net")
        country_codes.append("US")
        location_types.append("<MISSING>")
        store_numbers.append("<MISSING>")

    # This section calls to the map page to extract the latitudes and longitudes view regex
    response = session.get(
        "https://www.google.com/maps/d/viewer?mid=1k_5K2ikpmcAyElx_ND0io5MT-3w&ll=35.64271937457243%2C-88.47843979999999&z=4"
    ).text

    json_objects = extract_json(response.split("var _pageData = ")[1].replace("\\", ""))

    for location in json_objects[0][1][6][0][4][0][6]:
        latitude = location[4][0][1][0]
        longitude = location[4][0][1][1]
        latitudes.append(latitude)
        longitudes.append(longitude)

    df = pd.DataFrame(
        {
            "locator_domain": locator_domains,
            "page_url": page_urls,
            "location_name": names,
            "latitude": latitudes,
            "longitude": longitudes,
            "street_address": addresses,
            "city": citys,
            "state": states,
            "zip": zips,
            "phone": phones,
            "hours_of_operation": hours,
            "country_code": country_codes,
            "location_type": location_types,
            "store_number": store_numbers,
        }
    )

    for row in df.iterrows():

        yield {
            "locator_domain": row[1]["locator_domain"],
            "page_url": row[1]["page_url"],
            "location_name": row[1]["location_name"],
            "latitude": row[1]["latitude"],
            "longitude": row[1]["longitude"],
            "city": row[1]["city"],
            "store_number": row[1]["store_number"],
            "street_address": row[1]["street_address"],
            "state": row[1]["state"],
            "zip": row[1]["zip"],
            "phone": row[1]["phone"],
            "location_type": row[1]["location_type"],
            "hours": row[1]["hours_of_operation"],
            "country_code": row[1]["country_code"],
        }


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"]),
        page_url=sp.MappingField(mapping=["page_url"]),
        location_name=sp.MappingField(mapping=["location_name"]),
        latitude=sp.MappingField(mapping=["latitude"], part_of_record_identity=True),
        longitude=sp.MappingField(mapping=["longitude"], part_of_record_identity=True),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], is_required=False
        ),
        city=sp.MappingField(mapping=["city"]),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MultiMappingField(mapping=["zip"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"]),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(mapping=["store_number"]),
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
