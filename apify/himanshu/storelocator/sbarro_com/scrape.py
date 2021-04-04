import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import usaddress

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
    addressess = []
    base_url = "https://sbarro.com"
    UsState = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    ]

    location_url = (
        "https://sbarro.com/locations/?user_search=62232&radius=2100&unit=MI&count=All"
    )
    soup = bs(session.get(location_url).text, "lxml")

    for link in soup.find_all("section", {"class": "locations-result"}):
        page_url = base_url + link.find("a")["href"]
        if page_url.split("/")[-1]:
            try:
                location_name = link.find("h1", {"class": "location-name"}).text.strip()
            except:
                location_name = link.find("h2", {"class": "location-name"}).text.strip()

            addr = list(
                link.find("p", {"class": "location-address nobottom"}).stripped_strings
            )

            if len(addr) == 1:
                address = usaddress.parse(addr[0])

                street_address = []
                city = ""
                state = ""
                zipp = ""
                for info in address:
                    if "SubaddressType" in info:
                        street_address.append(info[0])

                    if "SubaddressIdentifier" in info:
                        street_address.append(info[0])

                    if "Recipient" in info:
                        street_address.append(info[0])

                    if "International" in info:
                        street_address.append(info[0])

                    if "BuildingName" in info:
                        street_address.append(info[0])

                    if "AddressNumber" in info:
                        street_address.append(info[0])

                    if "StreetNamePreDirectional" in info:
                        street_address.append(info[0])

                    if "StreetNamePreType" in info:
                        street_address.append(info[0])
                    if "StreetName" in info:
                        street_address.append(info[0])
                    if "StreetNamePostType" in info:
                        street_address.append(info[0])
                    if "StreetNamePostDirectional" in info:
                        street_address.append(info[0])
                    if "OccupancyType" in info:
                        street_address.append(info[0])
                    if "OccupancyIdentifier" in info:
                        street_address.append(info[0])

                    if "PlaceName" in info:
                        city = info[0]
                    if "StateName" in info:
                        state = info[0]
                    if "ZipCode" in info:
                        zipp = info[0]

                street_address = " ".join(street_address)
            else:
                street_address = " ".join(addr[:-1])
                city = addr[-1].split(",")[0]
                try:
                    if len(addr[-1].split(",")[1].split()) == 2:
                        state = addr[-1].split(",")[1].split()[0]
                        zipp = addr[-1].split(",")[1].split()[-1]
                    else:
                        state = addr[-1].split(",")[1].split()[0]
                        zipp = "<MISSING>"
                except:
                    pass

            if link.find("div", {"class": "location-phone location-cta"}):
                phone = (
                    link.find("div", {"class": "location-phone location-cta"})
                    .find("span", {"class": "btn-label"})
                    .text.strip()
                )

            else:
                phone = "<MISSING>"

            store_number = link["id"].split("-")[-1].strip()
            lat = link["data-latitude"]
            if lat == "0":
                lat = "<MISSING>"

            lng = link["data-longitude"]
            if lng == "0":
                lng = "<MISSING>"

            location_type = "Restaurant"
            try:
                location_soup = bs(session.get(page_url).text, "lxml")
                hours = " ".join(
                    list(
                        location_soup.find(
                            "div", {"class": "location-hours"}
                        ).stripped_strings
                    )
                ).replace("Hours of Operation", "")
                if "Hours not available" in hours:
                    hours = "<MISSING>"
            except:
                hours = "<MISSING>"
            if state in UsState:
                store = []
                store.append(base_url)
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)
                store.append("US")
                store.append(store_number)
                store.append(phone)
                store.append(location_type)
                store.append(lat)
                store.append(lng)
                store.append(hours)
                store.append(page_url)
                if street_address in addressess:
                    continue
                addressess.append(street_address)
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
