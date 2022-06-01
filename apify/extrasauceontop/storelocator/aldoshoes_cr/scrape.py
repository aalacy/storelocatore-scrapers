from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp
import re
import pandas as pd


def get_data():
    df = pd.read_csv("country_list.csv")
    country_url_list = df["Locator_url"].to_list()
    url_end = "/results?latitude=1&longitude=1&q="

    for country_url in country_url_list:
        url = country_url + url_end
        session = SgRequests()
        response = session.get(url).text

        soup = bs(response, "html.parser")

        try:
            grids = soup.find(
                "table", attrs={"class": "store-finder-results-table"}
            ).find_all("tr")[1:]
        except Exception:
            continue

        lat_lon_parts = response.split("LatLng(")[1:]

        x = 0
        for grid in grids:
            locator_domain = "aldoshoes.cr"
            page_url = (
                "https://www.aldoshoes.com"
                + grid.find("span", attrs={"class": "store-maplink"})
                .find("a")["href"]
                .split("?")[0]
            )
            location_name = grid.find(
                "span", attrs={"class": "store-location"}
            ).text.strip()
            address_parts = (
                str(grid.find_all("td")[2])
                .replace("<td>", "")
                .replace("</td>", "")
                .replace("<br/>", "<br>")
                .replace("</br>", "<br>")
                .replace("\n", "")
                .split("<br>")
            )

            address_parts = [x for x in address_parts if x]

            if bool(re.search(r"\d", address_parts[-1])) is True:

                address = "".join(part + " " for part in address_parts[:-2])
                city = address_parts[-2]
                zipp = address_parts[-1]
                state = "<MISSING>"

            else:

                address = "".join(part + " " for part in address_parts[:-1])
                city = address_parts[-1]
                state = "<MISSING>"
                zipp = "<MISSING>"

            if len(address_parts) == 2:
                if len(address_parts[0]) > len(address_parts[1]):
                    address = address_parts[0]
                    city = address_parts[1]
                    state = "<MISSING>"
                    zipp = "<MISSING>"

                else:
                    address = address_parts[1]
                    city = address_parts[0]
                    state = "<MISSING>"
                    zipp = "<MISSING>"

            country_code = page_url.split("/")[-4]
            phone = (
                grid.find("span", attrs={"class": "phone"})
                .text.strip()
                .split("ext")[0]
                .strip()
            )
            store_number = page_url.split("store/")[1].split("?")[0]
            location_type = "<MISSING>"

            lat_lon_part = lat_lon_parts[x]

            latitude = lat_lon_part.split(",")[0]
            longitude = lat_lon_part.split(",")[1].split(")")[0]

            x = x + 1

            hours = (
                grid.find("td", attrs={"class": "store-hours"})
                .text.strip()
                .replace("\n", "")
                .replace("\t", "")
                .replace("\r", "")
            )
            hours = re.sub("\s+", " ", hours)  # noqa

            if "ACCESSORIES" in location_name:
                continue

            if "coming soon" in "".join(part + " " for part in address_parts).lower():
                continue

            yield {
                "locator_domain": locator_domain.replace("\n", ""),
                "page_url": page_url.replace("\n", ""),
                "location_name": location_name.replace("\n", ""),
                "latitude": latitude.replace("\n", "").replace(" ", ""),
                "longitude": longitude.replace("\n", "").replace(" ", ""),
                "city": city.replace("\n", ""),
                "store_number": store_number.replace("\n", ""),
                "street_address": address.replace("\n", ""),
                "state": state.replace("\n", ""),
                "zip": zipp.replace("\n", ""),
                "phone": phone.replace("\n", ""),
                "location_type": location_type.replace("\n", ""),
                "hours": hours.replace("\n", ""),
                "country_code": country_code.replace("\n", ""),
            }


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"], is_required=False),
        page_url=sp.MappingField(mapping=["page_url"], is_required=False),
        location_name=sp.MappingField(
            mapping=["location_name"], part_of_record_identity=True
        ),
        latitude=sp.MappingField(mapping=["latitude"], part_of_record_identity=True),
        longitude=sp.MappingField(mapping=["longitude"], part_of_record_identity=True),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], part_of_record_identity=True
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
