from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp


def get_data():
    session = SgRequests()
    url = "https://www.bricomarche.com/magasins"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }

    response = (
        session.get(url, headers=headers).text.replace("&nbsp;", " ").replace("é", "e")
    )

    soup = bs(response, "html.parser")
    grids = soup.find_all(
        "div", attrs={"class": "GeolocResultItem GeolocResultItem-container-item"}
    )
    for grid in grids:
        locator_domain = "https://www.bricomarche.com"
        page_url = locator_domain + grid.find("a")["href"]
        location_name = grid.find("span").text.strip()
        city = location_name
        zipp = (
            grid.find("div", attrs={"class": "GeolocResultItem-textContent"})
            .find("div")
            .find_all("div")[1]
            .text.strip()
            .split(" ")[0]
        )
        store_number = page_url.split("/")[-1]
        address = (
            grid.find("div", attrs={"class": "GeolocResultItem-textContent"})
            .find("div")
            .find("div")
            .text.strip()
        )
        state = "<MISSING>"
        location_type = "<MISSING>"
        country_code = "FR"

        location_response = session.get(page_url, headers=headers).text.replace(
            "&nbsp;", " "
        )
        location_soup = bs(location_response, "html.parser")

        phone = location_response.split('"telephone": "')[1].split('"')[0]
        latitude = location_response.split('latitude": "')[1].split('"')[0]
        longitude = location_response.split('longitude": "')[1].split('"')[0]

        days = location_soup.find_all(
            "span", attrs={"class": "StoreDetails-scheduleDay"}
        )
        times = location_soup.find_all(
            "p", attrs={"class": "StoreDetails-scheduleTime"}
        )

        hours = ""
        for x in range(len(days)):
            day = (str(days[x]).split(">")[1].split("<")[0]).strip()
            time = (str(times[x]).split(">")[1].split("<")[0]).strip()
            hours = hours + day + " " + time + ", "

        hours = hours[:-2]

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
