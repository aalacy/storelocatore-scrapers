import csv

from bs4 import BeautifulSoup

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        for row in data:
            writer.writerow(row)


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    api_link = "https://www.cemex.co.uk/find-your-location.aspx?p_p_id=CEMEX_MAP_SEARCH&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=findTheNearestLocations&p_p_cacheability=cacheLevelPage&_CEMEX_MAP_SEARCH_locationName=Great%20Britain"
    stores = session.get(api_link, headers=headers).json()["theNearestLocations"]

    locator_domain = "cemex.co.uk"

    for store in stores:
        location_name = store["locationName"]
        street_address = store["locationAddress"]["locationStreet"].strip()
        city = store["locationAddress"]["locationCity"].strip()
        state = store["locationAddress"]["locationRegion"].strip()
        zip_code = store["locationAddress"]["locationPostcode"].strip()
        country_code = "GB"
        store_number = "<MISSING>"

        latitude = store["locationAddress"]["locationCoordinates"]["latitude"]
        longitude = store["locationAddress"]["locationCoordinates"]["longitude"]

        hours_of_operation = store["openingHours"]
        location_type = ", ".join(store["productList"])
        phone = store["locationContact"]["locationOrdersPhone"]
        if store["url"]:
            link = "https://www.cemex.co.uk" + store["url"]
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            if not phone:
                phone = base.find(class_="b-map-detail__phones").a.text
            if not location_type:
                location_type = base.find(
                    class_="b-map-detail__list-services"
                ).text.strip()
            if not hours_of_operation or hours_of_operation == "Closed":
                hours_of_operation = (
                    base.find(class_="b-map-detail__phones")
                    .find_all("div")[-1]
                    .text.replace("Opening Hours", "")
                    .split(" Get")[0]
                    .strip()
                )
                if (
                    "day" not in hours_of_operation
                    and "pm" not in hours_of_operation
                    and "24" not in hours_of_operation
                ):
                    hours_of_operation = "<MISSING>"
        else:
            link = "https://www.cemex.co.uk/find-your-location.aspx"
            phone = "<MISSING>"

        if not location_type:
            location_type = "<MISSING>"

        # Store data
        yield [
            locator_domain,
            link,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
