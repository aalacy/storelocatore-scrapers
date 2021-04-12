import csv
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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

    base_link = "https://massagegreenspa.com/sabai/directory?category=0&zoom=12&is_mile=1&directory_radius=25&view=list&hide_searchbox=0&hide_nav=1&hide_nav_views=0&hide_pager=0&featured_only=0&feature=1&perpage=99&list_map_show=1&sort=distance&is_geolocate=1&center=&__ajax=%23sabai-embed-wordpress-shortcode-1%20.sabai-directory-geolocate&_=1617952251926"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = base.find_all(class_="sabai-col-xs-9 sabai-directory-main")
    locator_domain = "massagegreenspa.com"

    for item in items:
        link = item.a["href"]
        location_name = (
            "Massage Green SPA "
            + item.find(class_="sabai-directory-title").text.split(",")[0].strip()
        )

        raw_address = (
            item.find(class_="sabai-directory-location")
            .text.replace("Ave Norwalk", "Ave, Norwalk")
            .replace("03 Queen", "03, Queen")
            .strip()
            .split(",")
        )
        street_address = raw_address[0].strip()
        city = raw_address[1].strip()
        state = raw_address[-1].split()[0]
        zip_code = raw_address[-1].split()[1]
        country_code = "US"
        store_number = item.a["class"][1].split("-")[-1]
        location_type = "<MISSING>"
        phone = item.find(itemprop="telephone").text.strip()
        if not phone:
            phone = "<MISSING>"
        hours_of_operation = "<MISSING>"

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        try:
            latitude = re.findall(
                r'lat":[0-9]{2}\.[0-9]+', str(base.find(id="sabai-inline-content-map"))
            )[0].split(":")[1][:10]
            longitude = re.findall(
                r'lng":-[0-9]{2,3}\.[0-9]+',
                str(base.find(id="sabai-inline-content-map")),
            )[0].split(":")[1][:10]
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        data.append(
            [
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
        )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
