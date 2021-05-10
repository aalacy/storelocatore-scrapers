import csv
import json

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

    base_link = "https://www.germainhotels.com/en/le-germain-hotel"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    # Get geo data to map with links
    j_data = []

    js = json.loads(base.find(id="__NEXT_DATA__").contents[0])["props"]["pageProps"][
        "initialApolloState"
    ]
    for j in js:
        if "hotel_Entry" in j:
            link = js[j]["uri"]
            if "le-germain-hotel" in link:
                geo = js[j]["geolocation"]
                j_data.append([link, geo["lat"], geo["lng"]])

    data = []
    items = base.find_all(class_="css-trxm7q e43cxw10")

    locator_domain = "germainhotels.com"

    for item in items:
        if "le-germain-" in item.a["href"]:
            link = "https://www.germainhotels.com" + item.a["href"]
        else:
            continue

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.find(class_="css-zq9h6m e14dtdjb2").get_text(" ").strip()

        raw_address = base.find(class_="css-1kzaqml e14dtdjb3").text.split(",")
        if len(raw_address) > 4:
            street_address = raw_address[0].strip() + " " + raw_address[1].strip()
        else:
            street_address = raw_address[0]

        city = raw_address[-3].strip()
        state = raw_address[-2].strip()
        zip_code = raw_address[-1].strip()
        if zip_code == "TG2 0G1":
            zip_code = "T2G 0G1"
        if zip_code == "K1P OC8":
            zip_code = "K1P 0C8"

        country_code = "CA"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        phone = base.find(class_="css-1uolpp8 e14dtdjb6").text.strip()

        latitude = "<MISSING>"
        longitude = "<MISSING>"

        for j in j_data:
            if j[0] in link:
                latitude = j[1]
                longitude = j[2]
                break

        hours_of_operation = "<MISSING>"

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
