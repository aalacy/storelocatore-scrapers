import csv

from bs4 import BeautifulSoup

from sgrequests import SgRequests


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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://www.mallorygroup.com/"

    data = []
    locator_domain = "mallorygroup.com"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    all_scripts = base.find_all("script")
    for script in all_scripts:
        if "var locationinfo" in str(script):
            break

    items = script.contents[0].split("locationinfo=")[1].split(",];")[0].split("],")
    for i in items:
        if "marker-mallory" not in i:
            continue
        item = i.split('mallory">')[1].split("</div>")[0]
        raw_data = list(BeautifulSoup(item, "lxml").stripped_strings)
        if "phone" in item.lower():
            for i, row in enumerate(raw_data):
                if "phone" in row.lower():
                    phone = raw_data[i + 1]
                    raw_data = list(BeautifulSoup(item, "lxml").stripped_strings)[:i]
                    break
        else:
            phone = "<MISSING>"

        location_name = "Mallory Location"

        street_address = " ".join(raw_data[:-1])
        if not street_address:
            street_address = "<MISSING>"
        city_line = raw_data[-1].split(",")
        city = city_line[0].strip()
        try:
            state = city_line[-1].strip().split()[0].strip()
        except:
            state = "<MISSING>"
        try:
            zip_code = city_line[-1].strip().split()[1].strip()
        except:
            zip_code = "<MISSING>"
        country_code = "US"
        if "MX" in str(city_line):
            country_code = "MX"
        if "Shanghai" in state:
            street_address = street_address + " " + city
            city = state
            state = "<MISSING>"
            country_code = "China"
        if "CN" in state:
            country_code = "China"
            state = "<MISSING>"
        if "Hong" in state:
            state = "Hong Kong"
            zip_code = "<MISSING>"
            country_code = "China"
        location_type = "<MISSING>"
        store_number = "<MISSING>"
        hours_of_operation = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"

        # Store data
        data.append(
            [
                locator_domain,
                "https://www.mallorygroup.com/#locations",
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
