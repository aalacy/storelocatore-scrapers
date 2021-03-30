import csv
from bs4 import BeautifulSoup
from sgrequests import SgRequests
import re

MISSING = "<MISSING>"
session = SgRequests()


def get_locations():
    viewmodel = session.get(
        "https://siteassets.parastorage.com/singlePage/viewerViewModeJson?&isHttps=true&isUrlMigrated=true&metaSiteId=4fb1a8a3-6d99-4330-b844-2d336bff969a&quickActionsMenuEnabled=false&siteId=023f2d1c-56de-438a-91d6-0b7a4fa6f584&v=3&pageId=5eaf97_92e55dbfa2e20f2249a6b7f6033465df_644&module=viewer-view-mode-json&moduleVersion=1.279.0&viewMode=desktop&dfVersion=1.1027.0"
    ).json()

    document_data = viewmodel.get("data").get("document_data")

    for key, item in document_data.items():
        locations_matcher = re.compile("locations", re.IGNORECASE)
        label = item.get("label", None)

        if label and locations_matcher.match(label):
            location_menu_items = item.get("items")

    if not location_menu_items:
        raise Exception("cannot find locations")

    menu_keys = [item.replace("#", "") for item in location_menu_items]
    link_keys = [
        document_data.get(item).get("link").replace("#", "") for item in menu_keys
    ]
    page_items = [
        document_data.get(key).get("pageId").replace("#", "") for key in link_keys
    ]

    page_links = [document_data.get(key).get("pageUriSEO") for key in page_items]

    return [f"https://www.mystricklands.com/{location}" for location in page_links]


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "location_type",
                "store_number",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "latitude",
                "longitude",
                "phone",
                "hours_of_operation",
            ]
        )
        # Body
        for row in data:
            if row:
                writer.writerow(row)


def parse_geo(url):
    lon = re.findall(r"destination=[-?\d\.]*\,([-?\d\.]*)", url)[0]
    lat = re.findall(r"destination=(-?[\d\.]*)", url)[0]
    return lat, lon


def fetch_data():
    locator_domain = "mystricklands.com"
    page_urls = get_locations()

    for page_url in page_urls:
        response = session.get(page_url)
        bs4 = BeautifulSoup(response.text, features="lxml")

        matched = re.search(r"(\d+\s.+(?:,|\\n)?.*),\s(\w{2})\s(\d{5})", bs4.text)

        if not matched:
            yield None
            continue

        location_name = bs4.select_one("h2 span").text
        address = matched.group(1)
        address_city = re.split(r"\(.*\)|\\n", address)
        if len(address_city) == 2:
            street_address, city = address_city
        else:
            city = re.search("Stricklands in (.*)", location_name, re.IGNORECASE).group(
                1
            )
            street_address = re.sub(city, "", address_city[0], re.IGNORECASE)

        state = matched.group(2).upper()
        zipcode = matched.group(3)
        country_code = "US"

        phone_match = re.search(
            r"Phone:\s*\((\d{3})\).*(\d{3})-(\d{4})", bs4.text, re.IGNORECASE
        )
        phone = (
            f"{phone_match.group(1)}{phone_match.group(2)}{phone_match.group(3)}"
            if phone_match
            else MISSING
        )

        hours_title = bs4.select_one("p:-soup-contains(Hours)") or bs4.select_one(
            "p:-soup-contains(Open)"
        )

        if hours_title is None:
            continue

        if "Open" in hours_title.text:
            hours_of_operation = hours_title.text
        else:
            weekday_tag, weekend_tag, *rest = hours_title.fetchNextSiblings()

            weekday_hours = re.sub(r"\s\s*", " ", weekday_tag.text)
            weekend_hours = re.sub(r"\s\s*", " ", weekend_tag.text)

            hours_of_operation = f"{weekday_hours},{weekend_hours}"

        location_type = MISSING
        latitude = MISSING
        longitude = MISSING
        store_number = MISSING

        yield [
            locator_domain,
            page_url,
            location_name,
            location_type,
            store_number,
            street_address.strip(),
            city,
            state,
            zipcode,
            country_code,
            latitude,
            longitude,
            phone,
            hours_of_operation,
        ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
