from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
from sgscrape import simple_scraper_pipeline as sp


def get_data():

    session = SgRequests()
    state_url = "https://locations.whataburger.com/directory.html"

    response = session.get(state_url).text

    soup = bs(response, "html.parser")
    state_links = soup.find_all("a", attrs={"class": "Directory-listLink"})

    location_urls = []
    for a_tag in state_links:
        loc_count = (
            a_tag.find("span", attrs={"class": "Directory-listLinkText"})["data-count"]
            .replace("(", "")
            .replace(")", "")
        )

        if loc_count == "1":
            location_urls.append("https://locations.whataburger.com/" + a_tag["href"])

        else:
            state_url = "https://locations.whataburger.com/" + a_tag["href"]
            response = session.get(state_url).text

            state_soup = bs(response, "html.parser")
            city_links = state_soup.find_all("a", attrs={"class": "Directory-listLink"})

            for city_link in city_links:

                loc_count = (
                    city_link.find("span", attrs={"class": "Directory-listLinkText"})[
                        "data-count"
                    ]
                    .replace("(", "")
                    .replace(")", "")
                )

                if loc_count == "1":
                    location_urls.append(
                        "https://locations.whataburger.com/" + city_link["href"]
                    )

                else:
                    city_url = "https://locations.whataburger.com/" + city_link["href"]
                    response = session.get(city_url).text

                    location_soup = bs(response, "html.parser")
                    single_location_links = location_soup.find_all(
                        "a", attrs={"class": "Teaser-titleLink"}
                    )
                    for single_location_link in single_location_links:
                        location_urls.append(
                            "https://locations.whataburger.com/"
                            + single_location_link["href"]
                        )

    for location_url in location_urls:
        response = session.get(location_url).text
        soup = bs(response, "html.parser")

        locator_domain = "whataburger.com"
        page_url = location_url.replace("../", "")
        location_name = soup.find(
            "span", attrs={"itemprop": "name", "id": "location-name"}
        ).text
        address = soup.find("span", attrs={"class": "c-address-street-1"}).text
        city = soup.find("span", attrs={"class": "c-address-city"}).text
        state = page_url.split("/")[-3].upper()
        if len(state) > 3:
            state = page_url.split("/")[-4]
        zipp = soup.find("span", attrs={"class": "c-address-postal-code"}).text
        country_code = "US"
        store_number = location_name.split(" ")[-1].replace("#", "")
        phone = soup.find("div", attrs={"itemprop": "telephone"}).text
        location_type = "<MISSING>"
        latitude = soup.find("meta", attrs={"itemprop": "latitude"})["content"]
        longitude = soup.find("meta", attrs={"itemprop": "longitude"})["content"]

        hour_sections = soup.find("div", attrs={"class": "HoursToday-dineIn"}).find(
            "span"
        )["data-days"]
        hour_sections = json.loads(hour_sections)

        hours = ""
        for section in hour_sections:
            try:
                day = section["day"]
                start = section["intervals"][0]["start"]
                end = section["intervals"][0]["end"]
                hours = hours + day + " " + str(start) + "-" + str(end) + ", "
            except Exception:
                day = section["day"]
                hours = hours + day + " closed" + ", "

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
            mapping=["location_name"],
        ),
        latitude=sp.MappingField(
            mapping=["latitude"],
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
        ),
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
