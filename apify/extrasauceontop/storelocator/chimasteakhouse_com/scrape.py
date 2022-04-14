from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp
import unidecode


def get_data():
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    session = SgRequests()
    url = "https://www.chimasteakhouse.com/"
    response = session.get(url, headers=headers).text

    soup = bs(response, "html.parser")
    links = soup.find_all("a", attrs={"class": "mega-menu-link"})

    page_urls = []
    for link in links:
        try:
            if "location" in link["href"]:
                page_urls.append(link["href"])
        except Exception:
            pass

    for page_url in page_urls:
        location_response = (
            session.get(page_url, headers=headers)
            .text.replace("<br />", "\n")
            .replace("<br>", "\n")
        )
        location_soup = bs(location_response, "html.parser")

        locator_domain = "www.chimasteakhouse.com"

        address_parts = location_soup.find(
            "div", attrs={"class": "content"}
        ).text.strip()

        location_name = city = address_parts.split("\n")[1].split(", ")[0]
        store_number = "<MISSING>"
        address = address_parts.split("\n")[0]
        state = address_parts.split("\n")[1].split(", ")[1].split(" ")[0]
        zipp = address_parts.split("\n")[1].split(", ")[1].split(" ")[1]
        phone = location_soup.find("a", attrs={"class": "big-font"}).text.strip()
        location_type = "<MISSING>"
        hours_bits = location_soup.find_all("p", attrs={"class": "small-font"})

        hours_parts = []
        for part in hours_bits:
            if (
                "dinner:" in part.text.strip().lower()
                or "lunch" in part.text.strip().lower()
            ):
                hours_parts.append(part)

        hours = ""
        for part in hours_parts:
            for bit in part.text.strip().split("\n"):
                hours = hours + bit + ", "

        hours = unidecode.unidecode(hours[:-2]).replace(":,", ":")

        lat_lon_part = location_soup.find(
            "iframe", attrs={"height": "450", "width": "600"}
        )["data-src"]

        latitude = lat_lon_part.split("!1d")[1].split("!2d")[0]
        longitude = lat_lon_part.split("!1d")[1].split("!2d")[1].split("!3")[0]

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
