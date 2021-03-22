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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here

    session = SgRequests()

    base_link = "https://www.mydrdental.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    req = session.get(base_link, headers=headers)

    base = BeautifulSoup(req.text, "lxml")
    items = base.findAll("div", attrs={"class": "address"})

    data = []
    for item in items:
        locator_domain = "mydrdental.com"
        location_name = item.find("h3").text.strip()
        raw_data = item.find("p").text.replace("<div>\r\n ", "").strip().split("\n")

        if len(raw_data) == 2:
            street_address = raw_data[0].strip()
            zip_code = raw_data[1][raw_data[1].rfind(" ") + 1 :].strip()
            state = raw_data[1][
                raw_data[1].rfind(" ") - 2 : raw_data[1].rfind(" ")
            ].strip()
            city = raw_data[1][: raw_data[1].find(state)].replace(",", "").strip()
        else:
            street_address = base.find("span", attrs={"itemprop": "streetAddress"}).text
            city = base.find("span", attrs={"itemprop": "addressLocality"}).text
            state = base.find("span", attrs={"itemprop": "addressRegion"}).text
            zip_code = base.find("span", attrs={"itemprop": "postalCode"}).text

        if "Lyndhurst" in city:
            city = "Lyndhurst"
            state = "NJ"

        country_code = "US"
        link = item.find("a")["href"]
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        req = session.get(link, headers=headers)

        new_base = BeautifulSoup(req.text, "lxml")
        phone = new_base.findAll("span", attrs={"class": "mm-phone-number"})[1].text
        gps_link = new_base.find("a", attrs={"class": "directions"})["href"]
        latitude = gps_link[gps_link.find("=") + 1 : gps_link.find(",")].strip()
        longitude = gps_link[gps_link.find(",") + 1 :].strip()
        hours_of_operation = (
            new_base.find("ul", attrs={"class": "loc_hours"})
            .get_text(" ")
            .replace("  ", " ")
            .strip()
        )

        data.append(
            [
                locator_domain,
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
                link,
            ]
        )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
