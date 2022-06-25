from sgrequests import SgRequests
import ast
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp
import unidecode

def get_data():
    url = "https://www.cosmo-gmbh.de/standorte"
    with SgRequests() as session:
        response = session.get(url).text
        list_object = ["['<div>COSMO" + part[:-1] + "</div>'" for part in response.split("['COSMO")[1:]]

        for location in list_object:
            locator_domain = "www.cosmo-gmbh.de"
            location_list = ast.literal_eval(location.split("],")[0] + "]")
            location_soup = bs(unidecode.unidecode(location_list[0].replace("<br />", "\n")), "html.parser")
            
            page_url = location_soup.find_all("a")[-1]["href"]
            location_name = location_soup.find("div").text.strip().split("\n")[0]

            latitude = location_list[1]
            longitude = location_list[2]
            city = "".join(part + " " for part in location_soup.find("div").text.strip().split("\n")[2].split(" ")[1:])
            store_number = "<MISSING>"
            address = location_soup.find("div").text.strip().split("\n")[1]
            state = "<MISSING>"
            zipp = location_soup.find("div").text.strip().split("\n")[2].split(" ")[0]
            phone = location_soup.find("div").text.strip().split("\n")[3]
            location_type = "<MISSING>"
            country_code = "DE"

            hours_response = unidecode.unidecode(session.get(page_url).text)
            hours_soup = bs(hours_response, "html.parser")
            hours = hours_soup.find_all("div", attrs={"class": "salons-two-column"})[-1].text.strip().replace("\n", "").split("iten:")[1].split("Taglich")[0].lower().replace("uhr", "uhr ")

            while "  " in hours:
                hours = hours.replace("  ", " ")

            hours = "".join(part + "uhr" for part in hours.split("uhr")[:-1])

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