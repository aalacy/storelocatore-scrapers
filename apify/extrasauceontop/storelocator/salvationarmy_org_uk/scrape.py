from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgscrape import simple_scraper_pipeline as sp


def get_data():
    search = DynamicZipSearch(country_codes=[SearchableCountries.BRITAIN])

    session = SgRequests()

    for zip_code in search:

        url = (
            "https://www.salvationarmy.org.uk/map-page?near%5Bvalue%5D="
            + str(zip_code)
            + "&near%5Bdistance%5D%5Bfrom%5D=40.22"
        )
        response = session.get(url).text

        soup = bs(response, "html.parser")

        grids = soup.find_all("div", attrs={"class": "geolocation-location js-hide"})
        location_grids = soup.find_all("div", attrs={"class": "e-grid-column"})
        website_grids = soup.find_all("a", attrs={"rel": "bookmark"})
        x = 0
        for grid in grids:
            locator_domain = "salvationarmy.org.uk"
            page_url = "salvationarmy.org.uk" + website_grids[x]["href"]
            country_code = "UK"

            location_name = grid.find(
                "p", attrs={"class": "field-content title"}
            ).text.strip()

            full_address = grid.find("p", attrs={"class": "address"}).text.strip()
            full_address = full_address.split("\n")
            full_address = [item.strip() for item in full_address]

            address = full_address[0]

            city_zipp = full_address[1].replace("  ", " ").replace(",", "").split(" ")

            city = ""
            zipp = ""

            for item in city_zipp:
                if re.search(r"\d", item) is None:
                    city = city + " " + item
                else:
                    zipp = zipp + " " + item

            zipp = zipp.strip()
            city = city.strip()

            latitude = grid["data-lat"]
            longitude = grid["data-lng"]

            state = "<MISSING>"

            phone_list = grid.find("a").text.strip()
            phone = ""
            for item in phone_list:
                if re.search(r"\d", item) is not None:
                    phone = phone + item
                if len(phone) == 11:
                    break

            if phone == "":
                phone = "<MISSING>"

            hours = "<MISSING>"

            store_number = grid["id"]

            location_grid = location_grids[x]
            location_type = location_grid.find("p").text.strip()
            search.found_location_at(latitude, longitude)
            x = x + 1

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
        latitude=sp.MappingField(
            mapping=["latitude"],
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
        ),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], part_of_record_identity=True
        ),
        city=sp.MappingField(mapping=["city"], part_of_record_identity=True),
        state=sp.MappingField(mapping=["state"], part_of_record_identity=True),
        zipcode=sp.MultiMappingField(mapping=["zip"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"]),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(mapping=["store_number"]),
        hours_of_operation=sp.MappingField(mapping=["hours"], is_required=False),
        location_type=sp.MappingField(
            mapping=["location_type"], part_of_record_identity=True
        ),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=get_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )
    pipeline.run()


scrape()
