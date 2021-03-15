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
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    base_url = "https://www.sagebrushsteakhouse.com/"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    for i in soup.find("ul", {"class": "subnavigation"}).find_all("a"):
        link = i["href"]
        location_soup = BeautifulSoup(
            session.get(link, headers=headers).content, "lxml"
        )

        try:
            address = (
                location_soup.find(id="ctl01_rptSpan_ctl00_pText")
                .text.replace(", NC,", ", NC")
                .replace("Blvd.", "Blvd,")
                .split(",")
            )
        except:
            continue

        street_address = address[0].strip()
        city = address[1].strip()
        state = address[2].split()[0].strip()
        zipp = address[2].split()[1].strip()
        phone = location_soup.find_all(id="ctl01_rptSpan_ctl00_pText")[1].text.split()[
            0
        ]

        raw_hours = location_soup.find_all(id="ctl01_rptSpan_ctl01_pText")
        hours = ""
        for hour in raw_hours:
            hours = (
                hours
                + " "
                + hour.text.split("Less")[0]
                .replace("\n", " ")
                .replace("\r", " ")
                .strip()
            ).strip()

        if "temporarily closed" in location_soup.h3.text.lower():
            hours = "Temporarily Closed"

        location_name = "SAGEBRUSH OF " + city
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours)
        store.append(link)

        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
