import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.baptistonline.org"
base_url = "https://www.baptistonline.org/locations"


def find_details(link, location_type, session):
    page_url = link.a["href"]
    if "google.com" in page_url or "tel:" in page_url:
        page_url = "<MISSING>"
    elif not page_url.startswith("http"):
        page_url = locator_domain + link.a["href"]
    addr = list(link.select_one("p.location-address").stripped_strings)
    phone = "<MISSING>"
    if link.select_one(".location-phone"):
        phone = link.select_one(".location-phone").text.strip()
    location_name = link.select_one(".location-name").text.strip()
    street_address = " ".join(addr[:-1])
    city = addr[-1].split(",")[0].strip()
    state = addr[-1].split(",")[1].strip().split(" ")[0].strip()
    zip_postal = addr[-1].split(",")[1].strip().split(" ")[-1].strip()
    country_code = "US"
    latitude = link.select_one('input[name="location-lat"]').get("value")
    longitude = link.select_one('input[name="location-lng"]').get("value")
    location_data = [
        locator_domain,
        page_url,
        location_name,
        street_address,
        city,
        state,
        zip_postal,
        country_code,
        "<MISSING>",
        phone,
        location_type,
        latitude,
        longitude,
        "<MISSING>",
    ]
    return location_data


def fetch_data():
    data = []
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=headers).text, "html.parser")
        links = soup.select("div#hospitals ul li")
        location_type = "hospital"
        for link in links:
            data.append(find_details(link, location_type, session))

        links = soup.select("div#minormedicalcenters ul li")
        location_type = "medical centers"
        for link in links:
            data.append(find_details(link, location_type, session))

        links = soup.select("div#clinics ul li")
        location_type = "clinics"
        for link in links:
            data.append(find_details(link, location_type, session))

        links = soup.select("div#specialtyfacilities ul li")
        location_type = "specialty facilities"
        for link in links:
            data.append(find_details(link, location_type, session))
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
