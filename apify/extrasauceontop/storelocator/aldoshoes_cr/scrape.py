from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp


def get_data():
    session = SgRequests()
    response = session.get(
        "https://www.aldoshoes.com/cr/es_CR/store-finder/results?latitude=29.6718062&longitude=-95.5543924&badResults=&q=10101&CSRFToken=84406638-ed58-4d8a-992d-e7e9a42a6ce4"
    ).text

    soup = bs(response, "html.parser")
    grids = soup.find("table", attrs={"class": "store-finder-results-table"}).find_all(
        "tr"
    )[1:]

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
        location_name = "ALDO"
        address_parts = (
            str(grid.find_all("td")[2])
            .replace("<td>", "")
            .replace("</td>", "")
            .replace("<br/>", "<br>")
            .split("<br>")
        )

        address = address_parts[1]
        city = address_parts[2].split(",")[0]
        state = "<MISSING>"
        try:
            zipp = address_parts[3]
            if "br" in zipp:
                zipp = "<MISSING>"
        except Exception:
            zipp = "<MISSING>"
        country_code = "CR"

        phone = grid.find("span", attrs={"class": "phone"}).text.strip()
        hours = "<MISSING>"
        store_number = page_url.split("store/")[1].split("?")[0]
        location_type = "<MISSING>"

        lat_lon_part = lat_lon_parts[x]

        latitude = lat_lon_part.split(",")[0]
        longitude = lat_lon_part.split(",")[1].split(")")[0]

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
        locator_domain=sp.MappingField(mapping=["locator_domain"], is_required=False),
        page_url=sp.MappingField(mapping=["page_url"], is_required=False),
        location_name=sp.MappingField(
            mapping=["location_name"], part_of_record_identity=True
        ),
        latitude=sp.MappingField(mapping=["latitude"], part_of_record_identity=True),
        longitude=sp.MappingField(mapping=["longitude"], part_of_record_identity=True),
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
