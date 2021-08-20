import csv
from bs4 import BeautifulSoup
from sgselenium import SgChrome


def write_output(data):
    with open("data.csv", newline="", mode="w", encoding="utf-8") as output_file:
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
    return_main_object = []
    # it will used in store data.
    locator_domain = "https://www.kosama.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    url = "https://www.kosama.com/find"

    with SgChrome() as driver:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "lxml")
        content = soup.find("div", class_="content").find("div", {"id": "accordion"})
        for loc in content.find_all("ul", class_="state"):
            try:
                for li in loc.find_all("li"):
                    page_url = (
                        "https://www.kosama.com" + li.find("a", class_="panel")["href"]
                    )
                    location_name = li.find("div", class_="name").text.strip()
                    list_address = list(li.stripped_strings)
                    if len(list_address) > 4:
                        street_address = list_address[1] + " " + list_address[2]
                        city = list_address[3].split(",")[0].strip()
                        state = list_address[3].split(",")[-1].split()[0].strip()
                        zipp = list_address[3].split(",")[-1].split()[-1].strip()
                        phone = list_address[-1].strip()
                    else:
                        street_address = list_address[1].strip()
                        city = list_address[2].split(",")[0].strip()
                        state = list_address[2].split(",")[-1].split()[0].strip()
                        zipp = list_address[2].split(",")[-1].split()[-1].strip()
                        phone = list_address[-1].strip()

                    latitude = ""
                    longitude = ""

                    store = [
                        locator_domain,
                        location_name,
                        street_address,
                        city,
                        state,
                        zipp,
                        country_code,
                        store_number,
                        phone,
                        location_type,
                        latitude,
                        longitude,
                        hours_of_operation,
                        page_url,
                    ]
                    store = [
                        "<MISSING>" if x == "" or x == "Blank" else x for x in store
                    ]

                    return_main_object.append(store)
            except:
                pass

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
