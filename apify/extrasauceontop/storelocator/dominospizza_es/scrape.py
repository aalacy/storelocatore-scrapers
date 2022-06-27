from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp
import re


def check_response(response):
    try:
        if '<div id="mapa' not in response:
            return False

        else:
            return True

    except Exception:
        return False


def get_data():
    url = "https://www.dominospizza.es/tiendas-dominos-pizza"
    with SgRequests(
        response_successful=check_response,
        proxy_country="es",
    ) as session:
        response = session.get(url).text

    soup = bs(response, "html.parser")
    grids = soup.find("div", attrs={"id": "listaTiendas"}).find_all("ul")

    for grid in grids:
        locator_domain = "www.dominospizza.es/"
        page_url = (
            "https://www.dominospizza.es"
            + grid.find("a", attrs={"class": "nm"})["href"]
        )
        location_name = grid.find("span", attrs={"itemprop": "name"}).text.strip()
        latitude = grid.find("li")["data-latitude"]
        longitude = grid.find("li")["data-longitude"]

        address_parts = (
            grid.find("span", attrs={"id": "idLocalidad"}).text.strip().split(", ")
        )
        address_parts_rev = [ele for ele in reversed(address_parts)]
        state = address_parts[-1]

        if len(address_parts) > 2:
            for part in address_parts_rev:
                number_count = sum(c.isdigit() for c in part)
                if number_count == 5:
                    zipp_index = address_parts.index(part)

            if address_parts[zipp_index] == address_parts[-2]:
                if re.search("[a-zA-Z]", address_parts[zipp_index]) is True:
                    zipp = address_parts[zipp_index].split(" ")[0]
                    city = "".join(
                        part for part in address_parts[zipp_index].split(" ")[1:]
                    )
                else:
                    zipp = address_parts[zipp_index]
                    city = "<MISSING>"
            else:
                city = address_parts[-2]
                zipp = address_parts[zipp_index]

            address = "".join(part + " " for part in address_parts[:zipp_index])

        else:
            city = "<MISSING>"
            zipp = "<MISSING>"
            address = address_parts[0]
            state = "".join(i for i in state if not i.isdigit())

        country_code = "ES"
        store_number = (
            grid.find("p", attrs={"id": "tiendaMapaUbicacion"})
            .find("div")["id"]
            .replace("mapa-", "")
        )

        phone = grid.find("span", attrs={"itemprop": "telephone"}).text.strip()
        location_type = "<MISSING>"

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
