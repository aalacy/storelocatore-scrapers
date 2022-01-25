from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
from sgscrape import simple_scraper_pipeline as sp


def get_data():
    session = SgRequests()
    url = "https://vitalitybowls.com/all-locations/"

    response = session.get(url).text
    soup = bs(response, "html.parser")

    loc_urls = [
        a_tag["href"]
        for a_tag in soup.find_all("a", attrs={"class": "locationurl"})
        if "coming soon" not in a_tag.text.strip().lower()
    ]

    for page_url in loc_urls:
        if page_url == "https://vitalitybowls.com/san-jose-brokaw/":
            page_url = "https://vitalitybowls.com/locations/san-jose-brokaw/"
        if page_url == "https://vitalitybowls.com/las-vegas-centennial-hills/":
            page_url = "https://vitalitybowls.com/locations/las-vegas-centennial-hills/"
        if page_url == "https://vitalitybowls.com/san-jose-cherry-ave/":
            continue

        response = session.get(page_url).text
        soup = bs(response, "html.parser")
        locator_domain = "vitalitybowls.com"
        location_name = (
            soup.find("div", attrs={"class": "et_pb_row et_pb_row_0"})
            .text.strip()
            .split("\n")[0]
        )

        country_code = "US"
        store_number = "<MISSING>"
        try:
            phone_part = soup.text.strip().split("CONTACT")[1].split("Tel:")[1]
        except Exception:
            try:
                phone_part = soup.text.strip().split("CONTACT")[1].split("Phone:")[1]
            except Exception:
                try:
                    phone_part = (
                        soup.text.strip().split("STORE INFO")[1].split("Phone:")[1]
                    )
                except Exception:
                    try:
                        phone_part = (
                            soup.text.strip().split("CONTACT")[1].split("phone:")[1]
                        )
                    except Exception:
                        try:
                            phone_part = (
                                soup.text.strip().split("CONTACT")[1].split("Phone")[1]
                            )
                        except Exception:
                            phone_part = "<MISSING>"

        x = 0
        phone = ""
        for character in phone_part:

            if bool(re.search(r"\d", character)) is True:
                x = x + 1
                phone = phone + character
                if x == 10:
                    break

        location_type = "<MISSING>"
        longitude = response.split("!2d")[1].split("!3d")[0]
        latitude = response.split("!3d")[1].split("!")[0]

        hours_parts_maybe = soup.find_all("div", attrs={"class": "et_pb_text_inner"})

        for contender in hours_parts_maybe:
            if "hours" in contender.text.strip().lower():
                hours_parts = contender.text.strip().split("\n")[1:]
                break

        hours = ""
        for part in hours_parts:
            hours = hours + part + ", "

            if "Sun" in part:
                break

        hours = hours[:-2]

        if "coming soon" in hours.lower():
            continue

        address_parts = str(
            soup.find_all("div", attrs={"class": "et_pb_text_inner"})[1]
        ).split("<br/>")

        start = 0
        address = ""
        for part in address_parts[:-1]:
            for line in part.split("\n"):
                if start == 1:
                    line_parts = line.split(">")
                    for thing in line_parts:

                        try:
                            if thing[0] == "<":
                                continue

                        except Exception:
                            continue

                        address_bit = thing.split("<")[0]
                        address = address + " " + address_bit

                if "store info" in line.lower():
                    start = 1

        address = address.replace("\n", "").strip()

        city = address_parts[-1].split(",")[0].strip().split("\n")[-1].split("\r")[-1]
        try:
            city = city.split(">")[-1].strip()
        except Exception:
            pass

        state = address_parts[-1].split(", ")[1].split(" ")[0]
        zipp = address_parts[-1].split(", ")[1].split(" ")[1].split("<")[0]

        if address == "":
            address_parts = str(
                soup.find_all("div", attrs={"class": "et_pb_text_inner"})[1]
            ).split("\n")
            address = ""
            for part in address_parts[:-1]:
                for line in part.split("\n"):
                    if start == 1:
                        line_parts = line.split(">")
                        for thing in line_parts:

                            try:
                                if thing[0] == "<":
                                    continue

                            except Exception:
                                continue

                            address_bit = thing.split("<")[0]
                            address = address + " " + address_bit

                    if "store info" in line.lower():
                        start = 1

            address = (
                address.strip().replace("  ", " ").split(location_name.split("-")[0])[0]
            )

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
        log_stats_interval=1000,
    )
    pipeline.run()


scrape()
