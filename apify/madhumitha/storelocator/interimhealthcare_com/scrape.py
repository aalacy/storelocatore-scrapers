import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re

DOMAIN = "https://www.interimhealthcare.com"
MISSING = "<MISSING>"


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    session = SgRequests()

    data = []
    found = []
    url_list = [
        "https://www.interimhealthcare.com/locations",
        "https://www.interimhealthcare.com/locations/?page=2",
    ]
    for url in url_list:
        response = session.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        loc = soup.find(
            "span",
            attrs={
                "id": "p_lt_ctl04_pageplaceholder_p_lt_ctl03_OfficesBasicDatalist_ctl00"
            },
        )
        locations = loc.findAll("span", style=False)
        for tag in locations:
            location_name = tag.find(
                "a", attrs={"title": "Click to zoom in to this location on the map."}
            ).text.strip()
            if location_name == "" or location_name == 0:
                location_name = MISSING
            phone = tag.find("div", attrs={"class": "location-phone"}).text.strip()
            if phone == "" or phone == 0:
                phone = MISSING
            street_address = tag.find(
                "div", attrs={"class": "location-add-1"}
            ).text.strip()
            if street_address in found:
                break
            found.append(street_address)
            if street_address == "" or street_address == 0:
                street_address = MISSING
            loc_city = tag.find("div", attrs={"class": "location-city"}).text.strip()
            if loc_city == "" or loc_city == 0:
                zipcode = state = city = MISSING
            ad_list = re.split("[ ]+", loc_city)
            zipcode = ad_list[-1]
            state = ad_list[-2]
            city_name = ad_list[-3]
            city = re.sub(",", "", city_name)
            map_url = str(tag.find("script", attrs={"type": "text/javascript"}))
            lat = re.findall(r"[-+]?[0-9]*\.?[0-9]+", map_url)[-4]
            lon = re.findall(r"[-+]?[0-9]*\.?[0-9]+", map_url)[-3]
            country = "US"
            hours_of_operation = location_type = store_number = MISSING

            link = "https:" + tag.find(class_="location-website").a["href"]
            data.append(
                [
                    DOMAIN,
                    link,
                    location_name,
                    street_address,
                    city,
                    state,
                    zipcode,
                    country,
                    store_number,
                    phone,
                    location_type,
                    lat,
                    lon,
                    hours_of_operation,
                ]
            )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
