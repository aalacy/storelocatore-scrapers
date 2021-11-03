import csv

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

    base_link = "https://www.bestwaywholesale.co.uk/depots/all"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = base.find(class_="main").find("ul").find_all("a")
    locator_domain = "bestwaywholesale.co.uk"

    for item in items:
        location_name = item.text
        if "bestway" not in location_name.lower():
            continue
        link = "https://www.bestwaywholesale.co.uk" + item["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        raw_address = list(
            base.find(class_="depotloc-left").find_all("p")[3].stripped_strings
        )
        if "telephone" in raw_address[0].lower():
            raw_address = list(
                base.find(class_="depotloc-left").find_all("p")[2].stripped_strings
            )
        street_address = " ".join(raw_address[:-2])
        city = raw_address[-2].strip()
        state = "<MISSING>"
        zip_code = raw_address[-1].strip()
        country_code = "GB"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = base.find(id="main").a.text.strip()
        hours_of_operation = " ".join(base.table.stripped_strings)
        map_link = base.find(id="directionlink")["href"]
        # Maps
        req = session.get(map_link, headers=headers)
        maps = BeautifulSoup(req.text, "lxml")

        try:
            raw_gps = maps.find("meta", attrs={"itemprop": "image"})["content"]
            latitude = raw_gps[raw_gps.find("=") + 1 : raw_gps.find("%")].strip()
            longitude = (
                raw_gps[raw_gps.find("%") + 1 : raw_gps.find("&")]
                .strip()
                .replace("2C", "")
            )
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
