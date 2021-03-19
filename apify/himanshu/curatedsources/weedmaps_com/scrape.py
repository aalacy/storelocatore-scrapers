import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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

        for row in data:
            writer.writerow(row)


def fetch_data():
    address = []
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"
    }
    page = 1
    while True:
        loc_url = (
            "https://api-g.weedmaps.com/discovery/v2/listings?&filter%5Bbounding_radius%5D=75000000mi&filter%5Bbounding_latlng%5D=32.79148101806641%2C-86.82768249511719&latlng=32.79148101806641%2C-86.82768249511719&page_size=150&page="
            + str(page)
        )
        jd = session.get(loc_url, headers=headers).json()
        page += 1
        if "errors" in jd.keys():
            break
        for loc in jd["data"]["listings"]:
            store = []
            location_name = loc["name"]
            street_address = loc["address"]
            if len(street_address.split(":")) > 1:
                continue
            city = loc["city"]
            state = loc["state"]
            temp_zipp = loc["zip_code"]
            a = temp_zipp.split("-")[0]
            if len(a) < 5:
                zipp = "<MISSING>"
            else:
                zipp = a
            temp_country_code = zipp
            if len(temp_country_code) == 5:
                country_code = "US"
            else:
                country_code = "CA"
            store_number = "<MISSING>"
            phone = loc["phone_number"]
            location_type = loc["type"]
            latitude = loc["latitude"]
            longitude = loc["longitude"]
            page_url = loc["web_url"]

            try:
                r = session.get(page_url)
                soup = BeautifulSoup(r.text, "lxml")
                temp_h_o_o = list(
                    soup.find(
                        "div",
                        class_="src__Box-sc-1sbtrzs-0 styled-components__DetailGridItem-sc-5o6q5l-0 styled-components__OpenHours-sc-5o6q5l-1 lfmwKQ",
                    ).stripped_strings
                )
                h_o_o = " ".join(temp_h_o_o).replace("Closed now", "")
            except:
                h_o_o = "<MISSING>"

            if (
                "https://weedmaps.com/dispensaries/tokyo-smoke-3003-danforth"
                == page_url
            ):
                state = "ON"
                zipp = "M4C 1M9"
            if (
                "https://weedmaps.com/dispensaries/dutch-love-toronto-theatre-district"
                == page_url
            ):
                state = "ON"
                zipp = "M5V 2E4"

            store.append("https://weedmaps.com/")
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append(store_number)
            store.append(phone)
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(h_o_o)
            store.append(page_url)
            if store[2] in address:
                continue
            address.append(store[2])
            store = [str(x).strip() if x else "<MISSING>" for x in store]
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
