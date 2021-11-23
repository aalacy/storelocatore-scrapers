import csv
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    }
    addresses = []

    base_url = locator_domain = "https://www.ziebartworld.com/"

    data = {
        "Longitude": "-71.1987762451",
        "Latitude": "46.8758392334",
        "callBack": "init_map",
        "telEnMobile": "1",
    }
    r_json = session.post(
        "https://www.uniglassplus.com/inc/ajax/rechSuccursale.cfm", data=data
    ).json()
    for data in r_json["ARRSUCCURSALE"]:
        location_name = data["SUCCURSALENOM"]
        street_address = data["ADRESSE"]
        city = data["VILLE"].split("(")[0].strip()
        state = data["PROVINCE"]
        zipp = data["CP"]
        country_code = "CA"
        store_number = data["SUCCURSALEID"]
        phone = data["TEL"]
        location_type = data["SUCCURSALETYPE"]
        latitude = data["POSLATITUDE"]
        longitude = data["POSLONGITUDE"]
        page_url = data["LIENDETAIL"]

        r1 = session.get(page_url)
        soup1 = BeautifulSoup(r1.text, "lxml")
        try:
            hours_of_operation = " ".join(
                list(soup1.find("div", {"id": "horaireSucc"}).stripped_strings)
            )
        except:
            hours_of_operation = "<MISSING>"
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

        if str(store[1]) + str(store[2]) not in addresses:
            addresses.append(str(store[1]) + str(store[2]))

            store = [str(x).strip() if x else "<MISSING>" for x in store]
            yield store

    # ----- us locations ------#

    addresses = []
    found = []

    max_distance = 1000

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=max_distance,
    )
    for zip_code in search:
        locator_domain = base_url
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "US"
        store_number = "<MISSING>"
        phone = ""
        location_type = "<MISSING>"
        latitude = ""
        longitude = ""
        page_url = ""
        hours_of_operation = ""

        page = 1
        while True:
            r = session.get(
                "https://www.ziebart.com/find-my-ziebart?zipcode="
                + str(zip_code)
                + "&distance="
                + str(max_distance)
                + "&page="
                + str(page),
                headers=headers,
            )
            soup = BeautifulSoup(r.text, "lxml")
            ul = soup.find("ul", class_="sfStoreList")
            if ul:
                for li in ul.find_all("li", class_="store-detail"):
                    page_url = (
                        "https://www.ziebart.com"
                        + li.find("div", class_="location-info-div").find("a")["href"]
                    )
                    if page_url in found:
                        continue
                    found.append(page_url)

                    location_name = (
                        li.find("div", class_="location-info-div")
                        .h4.text.split(",")[0]
                        .strip()
                    )
                    phone = li.find("span", class_="phone-digits").text.strip()
                    r1 = session.get(page_url, headers=headers)
                    soup1 = BeautifulSoup(r1.text, "lxml")
                    address = list(
                        soup1.find("div", class_="store-detail-text").stripped_strings
                    )
                    street_address = " ".join(address[:-1]).strip()
                    city = address[-1].split(",")[0].strip()
                    state = address[-1].split(",")[-1].split()[0].strip()
                    zipp = address[-1].split(",")[-1].split()[-1].strip()

                    try:
                        map_str = str(
                            soup1.find(class_="w-layout-grid grid-3 store-detail")
                        )
                        geo = re.findall(
                            r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", map_str
                        )[0].split(",")
                        latitude = geo[0]
                        longitude = geo[1]
                        search.found_location_at(latitude, longitude)
                    except:
                        latitude = "<INACCESSIBLE>"
                        longitude = "<INACCESSIBLE>"

                    hours_of_operation = (
                        " ".join(
                            list(
                                soup1.find_all("div", class_="store-detail-left")[
                                    -1
                                ].stripped_strings
                            )
                        )
                        .replace("Hours:", "")
                        .replace("Credit Cards Accepted", "")
                        .strip()
                    )
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
                    store = [str(x).strip() if x else "<MISSING>" for x in store]

                    if (str(store[2]) + str(store[-1])) in addresses:
                        continue
                    addresses.append(str(store[2]) + str(store[-1]))
                    yield store

                page += 1
            else:
                break


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
