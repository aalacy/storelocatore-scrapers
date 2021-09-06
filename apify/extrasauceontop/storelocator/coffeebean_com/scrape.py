from sgrequests import SgRequests
import pandas as pd
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp
import us


def get_data():
    session = SgRequests()

    base_url = "https://www.coffeebean.com/store-locator"

    # Country search
    locs = []
    for x in range(101):
        params = {"field_country_value": "USA", "page": x}
        r = session.get(base_url, params=params).text
        soup = bs(r, "html.parser")
        view_store = soup.find_all("a", attrs={"class": "view-store"})
        for item in view_store:
            locs.append(item["href"])

    # Lat Lng Boundary search
    base_url = "https://www.coffeebean.com/store-locator?field_geo_location_boundary%5Blat_north_east%5D=47.56&field_geo_location_boundary%5Blng_north_east%5D=69.44&field_geo_location_boundary%5Blat_south_west%5D=16.11&field_geo_location_boundary%5Blng_south_west%5D=-178.85"
    for x in range(101):
        params = {"page": x}

        r = session.get(base_url, params=params).text

        soup = bs(r, "html.parser")
        view_store = soup.find_all("a", attrs={"class": "view-store"})
        for item in view_store:
            locs.append(item["href"])

    # All search
    for x in range(101):
        url = "https://www.coffeebean.com/store-locator?&page=" + str(x)
        r = session.get(url).text
        soup = bs(r, "html.parser")
        view_store = soup.find_all("a", attrs={"class": "view-store"})
        for item in view_store:
            locs.append(item["href"])

    locs_df = pd.DataFrame({"locs": locs})
    locs_df = locs_df.drop_duplicates()
    locs = locs_df["locs"].to_list()

    for page_url in locs:
        if page_url == "https://www.coffeebean.com/node/1655":
            continue
        r = session.get(page_url).text
        soup = bs(r, "html.parser")

        locator_domain = "coffeebean.com"
        try:
            state = soup.find("span", attrs={"property": "addressRegion"}).text.strip()
        except Exception:
            try:
                state = soup.find(
                    "span", attrs={"itemprop": "addressRegion"}
                ).text.strip()
            except Exception:
                continue
        if us.states.lookup(state):
            country_code = "USA"
        else:
            continue

        try:
            location_name = soup.find("h1", attrs={"class": "Hero-title"}).text.strip()
        except Exception:
            location_name = soup.find(
                "span",
                attrs={
                    "class": "field field--name-title field--type-string field--label-hidden"
                },
            ).text.strip()

        try:
            latitude = soup.find("meta", attrs={"itemprop": "latitude"})["content"]
        except Exception:
            latitude = soup.find("meta", attrs={"property": "latitude"})["content"]

        try:
            longitude = soup.find("meta", attrs={"itemprop": "longitude"})["content"]
        except Exception:
            longitude = soup.find("meta", attrs={"property": "longitude"})["content"]

        try:
            city = soup.find(
                "span", attrs={"class": "Address-field Address-city"}
            ).text.strip()
        except Exception:
            city = soup.find("span", attrs={"property": "addressLocality"}).text.strip()
        store_number = "<MISSING>"
        try:
            address = soup.find(
                "span", attrs={"property": "streetAddress"}
            ).text.strip()
        except Exception:
            try:
                address = soup.find(
                    "span", attrs={"class": "Address-field Address-line1"}
                ).text.strip()
            except Exception:
                address = "<MISSING>"

        try:
            state = soup.find("span", attrs={"property": "addressRegion"}).text.strip()
        except Exception:
            state = soup.find("span", attrs={"itemprop": "addressRegion"}).text.strip()

        try:
            zipp = soup.find("span", attrs={"property": "postalCode"}).text.strip()
        except Exception:
            try:
                zipp = soup.find("span", attrs={"itemprop": "postalCode"}).text.strip()
            except Exception:
                zipp = "<MISSING>"

        phone = soup.find("span", attrs={"itemprop": "telephone"}).text.strip()
        if phone == "NULL":
            phone = "<MISSING>"
        location_type = "<MISSING>"

        days = soup.find_all("td", attrs={"class": "c-hours-details-row-day"})
        hour_parts = soup.find_all(
            "td", attrs={"class": "c-hours-details-row-intervals"}
        )

        count = 0
        hours = ""
        for day_part in days:
            day = day_part.text.strip()
            hour = hour_parts[count].text.strip()

            hours = hours + day + " " + hour + ", "
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
