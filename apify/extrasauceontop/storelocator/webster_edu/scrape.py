from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
from sgscrape import simple_scraper_pipeline as sp


def get_data():
    session = SgRequests()

    response = session.get(
        "https://webster.edu/catalog/current/graduate-catalog/campus-locations.html#.YRbMxIhKi3A"
    ).text

    response = response.split("Palais Wenkheim, 23 Praterstrasse")[0]
    soup = bs(response, "html.parser")

    p_tags = soup.find_all("p")

    address_p_list = []
    for tag in p_tags:
        if "Ph:" in tag.text.strip() in tag.text.strip():
            address_p_list.append(tag)

    name_tags = soup.find_all("strong")

    name_s_list = []
    for tag in name_tags:
        if (
            "^" in tag.text.strip()
            or "*" in tag.text.strip()
            or "Webster University at Southwestern Illinois College" in tag.text.strip()
            or "University Center of Lake County" in tag.text.strip()
        ):
            tag_check = tag.text.strip().replace("^", "")
            if tag_check == "*":
                tag = name_tags[name_tags.index(tag) - 1]
            name_s_list.append(tag)

    x = 0
    for tag in name_s_list:
        locator_domain = "webster.edu"
        page_url = "<MISSING>"
        location_name = tag.text.strip()

        address_parts = str(address_p_list[x]).split("<br/>")
        address_pieces = []
        begin = "False"
        for part in address_parts:
            if bool(re.search(r"\d", part)) is True:
                begin = "True"

            if begin == "True":
                address_pieces.append(part)

        for piece in address_pieces:
            if "Ph:" in piece:
                phone_index = address_pieces.index(piece)

        address = ""
        for y in range(phone_index + 1):
            if y <= phone_index - 2:
                address = address + address_pieces[y].replace("</strong>", "") + " "

            elif y == phone_index - 1:
                city_state = address_pieces[y]

            else:
                phone = address_pieces[y]

        address = address.strip()
        phone = phone.replace("Ph: ", "").split(",")[0]
        city = city_state.split(",")[0]
        state = city_state.split(", ")[1].split(" ")[0]
        zipp = city_state.split(", ")[1].split(" ")[1]

        latitude = "<MISSING>"
        longitude = "<MISSING>"
        store_number = ""
        location_type = ""
        hours = ""
        country_code = "US"

        yield {
            "locator_domain": locator_domain,
            "page_url": page_url,
            "location_name": location_name.replace("*", "").replace("^", ""),
            "latitude": latitude,
            "longitude": longitude,
            "city": city,
            "store_number": store_number,
            "street_address": address,
            "state": state,
            "zip": zipp[:5],
            "phone": phone,
            "location_type": location_type,
            "hours": hours,
            "country_code": country_code,
        }

        x = x + 1


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"], is_required=False),
        page_url=sp.MappingField(mapping=["page_url"], is_required=False),
        location_name=sp.MappingField(
            mapping=["location_name"], part_of_record_identity=True
        ),
        latitude=sp.MappingField(mapping=["latitude"], is_required=False),
        longitude=sp.MappingField(mapping=["longitude"], is_required=False),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], is_required=False
        ),
        city=sp.MappingField(mapping=["city"], part_of_record_identity=True),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MultiMappingField(mapping=["zip"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"], is_required=False),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(mapping=["store_number"], is_required=False),
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
