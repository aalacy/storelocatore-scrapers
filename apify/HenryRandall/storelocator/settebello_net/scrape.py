import csv
from sgselenium import SgSelenium
from bs4 import BeautifulSoup

driver = SgSelenium().chrome()
locator_domain = "https://www.settebello.net/"
link = "https://www.settebello.net/location-hours"


def fetch_data():
    driver.get(link)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    soup = soup.find_all("div", {"class": "col sqs-col-4 span-4"})
    locations = []
    for entry in soup:
        locations = locations + entry.find_all("div", {"class": "sqs-block-content"})

    data = []
    for location in locations:
        try:
            location_name = location.find("h3").text.strip()
            page_url = locator_domain[:-1] + location.find("a").get("href")
            text = location.find_all("p")
            street_address = text[0].text.strip()
            address2 = text[1].text.strip()
            [city, statezip] = address2.split(", ")
            statezip = statezip.split(" | ")[0]
            [state, postal] = statezip.split(" ")
            country_code = "US"
            store_number = "<MISSING>"
            phone = text[2].text.strip()
            location_type = "<MISSING>"
            coords = location.find_all("a")[1].get("href")
            coords = coords.split("@")[1].split(",")
            latitude = coords[0]
            longitude = coords[1]
            hours = text[3:]
            hoo = ""
            for hour in hours:
                if hour.text.strip() != "":
                    hoo = hoo + hour.text.strip() + ", "
            hoo = hoo.rsplit(",", 1)[0]

            row = [
                locator_domain,
                page_url,
                location_name,
                street_address,
                city,
                state,
                postal,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hoo,
            ]
            data.append(row)
        except:
            continue
    return data


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
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


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
