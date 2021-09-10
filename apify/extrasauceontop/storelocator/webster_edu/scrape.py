from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp
import json


def cross_check(location_name, session):

    response = session.get(
        "https://ousearch.omniupdate.com/texis/search/?pr=webster&rdepth=31&query="
        + location_name
        + "&jump=&uq=https://www.webster.edu/*&prox=page&sufs=0&order=r&rorder=500&rprox=750&rdfreq=500&rwfreq=750&rlead=750&coryMaddensCacheBuster"
    ).text
    response = (
        response.replace("\n", "")
        .replace("\t", "")
        .replace("ousearchresults(", "")[:-1]
    )

    final = json.loads(response)

    page_url = ""
    for result in final["results"]:
        url_to_check = result["url"]

        if "/locations/" in url_to_check and "/index.php" in url_to_check:
            page_url = url_to_check
            break

    if page_url == "":
        for result in final["results"]:
            url_to_check = result["url"]

            if "/locations/" in url_to_check:
                page_url = url_to_check
                break

    if page_url == "":
        response = session.get(
            "https://ousearch.omniupdate.com/texis/search/?pr=webster&rdepth=31&query="
            + location_name.split(" ")[0]
            + "&jump=&uq=https://www.webster.edu/*&prox=page&sufs=0&order=r&rorder=500&rprox=750&rdfreq=500&rwfreq=750&rlead=750&coryMaddensCacheBuster"
        ).text
        response = (
            response.replace("\n", "")
            .replace("\t", "")
            .replace("ousearchresults(", "")[:-1]
        )

        final = json.loads(response)
        for result in final["results"]:
            url_to_check = result["url"]

            if "/locations/" in url_to_check:
                page_url = url_to_check
                break

    return page_url


def get_data():
    session = SgRequests()

    response = session.get("https://legacy.webster.edu/locations/index.xml").text
    soup = bs(response, "html.parser")

    placemarks = soup.find_all("placemark")

    for placemark in placemarks:
        testmark = str(placemark)

        testmark = testmark[:-12]
        testmark = testmark[11:]

        if "placemark" in testmark.lower():
            continue

        locator_domain = "legacy.webster.edu"
        location_name = placemark.find("name").text.strip().replace("\n", "")
        latitude = placemark.find("coordinates").text.strip().split(",")[1]
        longitude = placemark.find("coordinates").text.strip().split(",")[0]

        address_parts = placemark.find("description").text.strip()
        phone = address_parts.split("Phone: ")[-1].strip()
        if location_name == "San Antonio":
            phone = phone.replace(" ", "")
        if " " in phone or "+" in phone or location_name == address_parts:
            continue

        address_pieces = address_parts.split("<br/>")

        if len(address_pieces) > 2:
            address_things = address_pieces[:-2]
            address = ""
            for piece in address_things:
                address = address + piece + " "

            address = address.strip()

            city = address_pieces[-2].split(", ")[0].strip()
            state = " " + address_pieces[-2].split(", ")[1].split(" ")[0].strip()
            zipp = address_pieces[-2].split(", ")[1].split(" ")[-1].strip()

        else:
            address = address_pieces[0].split(",")[0].strip()
            city = address_pieces[0].split(",")[1].strip()
            state = " " + address_pieces[0].split(",")[2].split(" ")[-2].strip()
            zipp = address_pieces[0].split(",")[2].split(" ")[-1].strip()

        city = city.replace("Â ", "")
        zipp = zipp.replace("Â ", "")
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        hours = "<MISSING>"
        country_code = "US"

        page_url = cross_check(location_name, session)
        page_response = session.get(page_url).text

        if (
            "permanently closed" in page_response.lower()
            or "This Webster University location is no longer open" in page_response
        ):
            continue

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
            "zip": zipp[:5],
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
        latitude=sp.MappingField(mapping=["latitude"], is_required=False),
        longitude=sp.MappingField(mapping=["longitude"], is_required=False),
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
