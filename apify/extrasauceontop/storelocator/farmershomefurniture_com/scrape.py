from sgrequests import SgRequests
from sgscrape import simple_scraper_pipeline as sp
from bs4 import BeautifulSoup as bs
import cloudscraper


def get_data():
    session = SgRequests()
    scraper = cloudscraper.create_scraper(sess=session)
    url = "https://secure.gotwww.com/gotlocations.com/microd/farmershomefurniture.com/index.php"
    params = {
        "brand": "",
        "MinZoom": "",
        "MaxDistance": "",
        "address": "96799",
        "bypass": "y",
        "Submit": "search",
        "language": "",
    }

    response = session.post(url, data=params).text
    lines = response.split("\n")

    good_lines = [line for line in lines if "L.marker" in line]

    for location in good_lines:
        locator_domain = "https://www.farmershomefurniture.com/"
        page_url = location.split('href="')[1].split('"')[0]
        location_name = location.split('target="new">')[1].split("<")[0]
        if location_name == "name":
            continue
        address = location.split("class=address>")[1].split("<")[0]
        city = location.split("class=city>")[1].split("<")[0].strip().replace(",", "")
        state = location.split("state>")[1].split(" <")[0]
        zipp = location.split("class=zip>")[1].split("<")[0]
        country_code = "US"
        try:
            store_number = location.split("mailto:Store")[1].split("@")[0]
        except Exception:
            store_number = "<MISSING>"
        phone = location.split('<a href="tel:')[1].split('"')[0]
        location_type = "<MISSING>"
        latitude = location.split("marker([")[1].split(",")[0]
        longitude = location.split(",")[1].split("]")[0]
        try:
            hours = location.split("hours: ")[1].split("<")[0]
        except Exception:
            try:
                hours_data = scraper.get(page_url).text
                hours_soup = bs(hours_data, "html.parser")
                hours = (
                    hours_soup.find("div", attrs={"class": "grid-30"})
                    .text.strip()
                    .split("Store Hours")[1]
                    .split("Email")[0]
                    .replace("\n", " ")
                )
            except Exception:
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
