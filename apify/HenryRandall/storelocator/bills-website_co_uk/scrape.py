from sgrequests import SgRequests
from sgzip.static import static_zipcode_list
from sgzip.dynamic import SearchableCountries
import csv


def find_locations():
    zipcodes = static_zipcode_list(radius=5, country_code=SearchableCountries.BRITAIN)
    session = SgRequests()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }

    url = "http://bills-website.co.uk/restaurants"
    r = session.get(url, headers=headers)
    token = r.text.split('<meta name="csrf-token" content="', 1)[1].split('">', 1)[0]

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRF-TOKEN": token,
        "Content-Type": "application/json;charset=utf-8",
        "X-XSRF-TOKEN": "eyJp",
    }

    ids = []
    locations = []
    for code in zipcodes:
        body = {"coords": None, "search": code}
        result = session.post(
            "https://bills-website.co.uk/ajax/locations", json=body, headers=headers
        ).json()
        try:
            result = result["result"]
            for location in result:
                id = location["id"]
                if id not in ids:
                    locations.append(location)
                    ids.append(id)
        except:
            pass

    return locations


def fetch_data(locations):
    url = "http://bills-website.co.uk"
    locations_data = []
    for location in locations:
        location_data = []
        if location["url"] is None:
            continue
        location_url = url + location["url"]
        session = SgRequests()
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
        }

        r = session.get(location_url, headers=headers)
        hoo = ""
        hours = r.text.split(
            "Hours&quot;,&quot;times&quot;:[{&quot;title&quot;:&quot;", 1
        )[1].split("&quot;}]}", 1)[0]
        hours = hours.split("},{")
        for hour in hours:
            hour = hour.split("&quot;")
            index = hour.index(",")
            index2 = hour.index("content")
            day = hour[index - 1]
            time = hour[index2 + 2]
            hour = day + " " + time
            hour = hour.replace("&amp;amp;", "&")
            hoo = hoo + hour + " "
        location_data.append(url)
        location_data.append(location_url)
        location_data.append(location["title"])
        address = location["meta"][0]["content"]
        city_zip = address.split(", ")[-1]
        street = address.split(", ")[0:-1]
        street = ", ".join(street)
        city = city_zip.split(" ")[0:-2]
        city = " ".join(city)
        if city == "":
            city = street.split(", ")[-1]
            street = street.split(", ")[0:-1]
            street = ", ".join(street)
        zip_code = city_zip.split(" ")[-2:]
        zip_code = " ".join(zip_code)
        if street == "":
            street = "<MISSING>"
            city = "<MISSING>"
            zip_code = "<MISSING>"
        location_data.append(street)
        location_data.append(city)
        location_data.append("<MISSING>")
        location_data.append(zip_code)
        location_data.append("<MISSING>")
        location_data.append(location["id"])
        location_data.append(location["meta"][1]["content"])
        location_data.append("<MISSING>")
        location_data.append("<MISSING>")
        location_data.append("<MISSING>")
        location_data.append(hoo)
        locations_data.append(location_data)
    return locations_data


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
    locations = find_locations()
    data = fetch_data(locations)
    write_output(data)


scrape()
