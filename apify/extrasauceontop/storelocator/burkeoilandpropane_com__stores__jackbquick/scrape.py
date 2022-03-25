from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp
import re


def get_data():
    session = SgRequests()
    response = session.get("https://www.burkeoilandpropane.com/stores/jackbquick").text
    soup = bs(response, "html.parser")

    grids = soup.find_all("div", attrs={"class": "_1KV2M"})[1:]
    location_names = []
    for grid in grids:
        try:
            location_name = grid.find("h3").text.strip()

        except Exception:
            continue

        if location_name not in location_names:
            location_names.append(location_name)

        else:
            continue

        locator_domain = "https://www.burkeoilandpropane.com/stores/jackbquick"
        page_url = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"

        spans = grid.find_all("span", attrs={"style": "font-size:16px;"})

        if len(spans) == 3:
            city = spans[-1].text.strip().split(", ")[0]

            address = spans[-2].text.strip()
            state = spans[-1].text.strip().split(", ")[1].split(" ")[0]
            try:
                zipp = spans[-1].text.strip().split(", ")[1].split(" ")[1]
            except Exception:
                zipp = "<MISSING>"

            phone = spans[0].text.strip().replace("Tel: ", "")

        elif len(spans) == 2:
            address = spans[-1].text.strip()
            city = (
                grid.find("p", attrs={"style": "font-size:16px; line-height:1.5em;"})
                .find("span")
                .text.strip()
            )
            state = (
                grid.find("p", attrs={"style": "font-size:16px; line-height:1.5em;"})
                .find_all("span")[-1]
                .text.strip()
                .split(" ")[-2]
            )
            zipp = (
                grid.find("p", attrs={"style": "font-size:16px; line-height:1.5em;"})
                .find_all("span")[-1]
                .text.strip()
                .split(" ")[-1]
            )
            phone = spans[0].text.strip().replace("Tel: ", "")

        else:
            address_parts = [
                part.replace(u"\xa0", u" ")
                for part in spans[0].text.strip().split("\n")
            ]
            address = address_parts[1]
            city = address_parts[-1].split(",")[0]
            state = address_parts[-1].split(", ")[1].split(" ")[0]
            zipp = address_parts[-1].split(", ")[1].split(" ")[1]
            phone = address_parts[0].replace("Tel: ", "")

        store_number = ""
        for character in location_name:
            if bool(re.search(r"\d", character)) is True:
                store_number = store_number + character

        if store_number == "":
            store_number = "<MISSING>"
        location_type = "<MISSING>"
        hours = "<MISSING>"
        country_code = "US"

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
        page_url=sp.MappingField(mapping=["page_url"]),
        location_name=sp.MappingField(
            mapping=["location_name"], part_of_record_identity=True
        ),
        latitude=sp.MappingField(mapping=["latitude"]),
        longitude=sp.MappingField(mapping=["longitude"]),
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
