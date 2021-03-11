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

    base_link = "https://www.immunotek.com/?sm-xml-search=1&lat=36.3716117&lng=-89.7153981&radius=0&namequery=36.3711471%2C%20-89.71921320000001&query_type=all&limit=0&locname&address&city&state&zip&pid=11279"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()

    data = []
    locator_domain = "immunotek.com"

    for store in stores:
        location_name = (
            "ImmunoTek " + store["name"].split(",")[0].replace("&#8211;", "-").strip()
        )
        link = store["permalink"].replace("/map/", "/location/")
        try:
            req = session.get(link, headers=headers)
        except:
            continue
        base = BeautifulSoup(req.text, "lxml")

        phone = base.find_all(style="text-align: center;")[1].text.strip()
        hours_of_operation = (
            base.find_all(style="text-align: center;")[-1]
            .text.encode("ascii", "replace")
            .decode()
            .replace("?", "-")
            .strip()
        )

        if "coming-soon" in str(base).lower():
            hours_of_operation = "Tuesday-Saturday 10am - 4pm"
            if "greenwood" in base.find(style="text-align: center;").text.lower():
                phone = "864-377-8115"
            elif "williamsport" in base.find(style="text-align: center;").text.lower():
                phone = "570-666-9290"
            elif "horn lake" in base.find(style="text-align: center;").text.lower():
                phone = "662-913-2506"
            else:
                continue

        street_address = (store["address"] + " " + store["address2"]).strip()
        city = store["city"]
        state = store["state"]
        zip_code = store["zip"]
        country_code = "US"
        store_number = store["ID"]
        location_type = "<MISSING>"
        latitude = store["lat"]
        longitude = store["lng"].split(",")[0]

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
