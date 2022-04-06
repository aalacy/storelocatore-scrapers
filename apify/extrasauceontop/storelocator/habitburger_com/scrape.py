from sgrequests import SgRequests
import json
from sgscrape import simple_scraper_pipeline as sp


def extract_json(html_string):
    json_objects = []
    count = 0

    brace_count = 0
    for element in html_string:

        if element == "{":
            brace_count = brace_count + 1
            if brace_count == 1:
                start = count

        elif element == "}":
            brace_count = brace_count - 1
            if brace_count == 0:
                end = count
                try:
                    json_objects.append(
                        json.loads(
                            html_string[start : end + 1]
                            .replace("\n", "")
                            .replace("\r", "")
                        )
                    )
                except Exception:
                    pass
        count = count + 1

    return json_objects


def get_data():
    session = SgRequests()

    url = "https://www.habitburger.com/locations/all/"
    all_stores = session.get(url).text

    url_parts = all_stores.split("latlng: {")

    page_urls_to_iterate = []
    coords = []
    for part in url_parts[1:]:
        url_part = part.split("post_name: '")[1].split("'")[0]
        lat_part = part.split("lat: ")[1].split(",")[0]
        lng_part = part.split("lng: ")[1].split("}")[0]
        coords.append([lat_part, lng_part])
        page_urls_to_iterate.append("https://www.habitburger.com/locations/" + url_part)

    x = 0
    for url in page_urls_to_iterate:
        x = x + 1
        locator_domain = "habitburger.com"

        response = session.get(url).text.replace(
            "https://habitburger.fbmta.com/shared/images/275/275_2021012818164353.jpg",
            "",
        )
        if "Coming Soon!" in response:
            continue
        json_objects = extract_json(response)
        location = json_objects[-1]

        location_name = location["address"]["addressLocality"]
        city = location_name
        state = location["address"]["addressRegion"]
        country_code = location["address"]["addressCountry"]
        zipp = location["address"]["postalCode"]

        if zipp == "":
            continue

        address = (
            location["address"]["streetAddress"]
            .replace(city + " " + state + " " + zipp, "")
            .strip()
        )

        address = address.replace("BlvdTerminal", "Blvd Terminal")
        store_number = "<MISSING>"

        try:
            phone = location["telephone"]
        except Exception:
            "<MISSING>"
        location_type = location["@type"]

        latitude = coords[x - 1][0]
        longitude = coords[x - 1][1]

        hours = location["openingHours"][0]
        if hours == "":
            check = response.split("Hours")[1].split("div")[0]

            if "Temporarily Closed" in response:
                hours = "Temporarily Closed"

            elif "Coming Soon" in response:
                hours = "Opening Soon"

            elif "Dining Room & Drive-Thru" in response:
                check = check.split("<br>")
                check = check[:-1]
                x = 0
                for section in check:
                    if x == 0:
                        x = 1
                        continue
                    hours = hours + section + ", "

            elif "Dining Room" in check:
                check = check.split("<br>")
                check = check[:-1]
                x = 0
                for section in check:
                    if x == 0:
                        x = 1
                        continue
                    if "h2" in section:
                        break
                    hours = hours + section + ", "

            elif len(check.split("\n")) == 2:
                check = check.split("\n")[1].split("<br>")

                for item in check:
                    hours = hours + item.rstrip() + " "

                hours = hours.replace("</", "").strip()
                hours = hours.strip()

            elif location_name == "Reno":
                check = check.split("\n")[1:]
                for item in check:
                    item = item.replace("\r", "")
                    item = (
                        item.replace('<h2 class="hdr">', "")
                        .replace('</h2 class="hdr"><br>', "")
                        .replace("<br>", "")
                        .replace("                        </", "")
                    )
                    hours = hours + item + " "

                hours = hours.strip()

            elif location_name == "Phoenix":
                hours = check.split("\n")[1].replace("<br>", "").strip()

        if "www.habitburger.com" in hours:
            hours = "Temporarily Closed"

        elif "Thru" in hours:
            hours = hours.split("Thru:")[1].strip()

        yield {
            "locator_domain": locator_domain,
            "page_url": url,
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
