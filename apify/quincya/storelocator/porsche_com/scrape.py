import csv

from bs4 import BeautifulSoup

from sgrequests import SgRequests

user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
headers = {"User-Agent": user_agent}

session = SgRequests()


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


def get_data(base_link):
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find("listoflocations").find_all("location")

    stores = []
    locator_domain = "porsche.com"
    for item in items:
        location_name = item.find("name").text.strip()
        street_address = item.find("street").text.replace("Côte", "Cote")
        city = item.find("city").text.strip()
        state = item.find("statecode").text.upper()
        zip_code = item.find("postcode").text
        if len(zip_code) == 4:
            zip_code = "0" + zip_code
        store_number = item.find("id").text
        location_type = "<MISSING>"
        latitude = item.find("coordinates").find("lat").text
        longitude = item.find("coordinates").find("lng").text.replace("E+07", "")
        phone = item.find("phone").text
        hours_of_operation = "<MISSING>"

        if "canada" in base_link:
            country_code = "CA"
        else:
            country_code = "US"

        link = item.find("url1").text
        phone = item.find("phone").text
        stores.append(
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
    return stores


def fetch_data():

    data = []

    states = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DC",
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

    for state in states:
        base_link = (
            "https://www.porsche.com/all/dealer2/GetLocationsWebService.asmx/GetLocationsInStateSpecialJS?market=usa&siteId=usa&language=none&state=&_locationType=Search.LocationTypes.Dealer&searchMode=state&searchKey=%s&address=&maxproximity=1000&maxnumtries=&maxresults=10000&postalcode="
            % (state)
        )

        res = get_data(base_link)
        if res:
            for r in res:
                data.append(r)

    ca_link = "https://www.porsche.com/all/dealer2/GetLocationsWebService.asmx/GetLocationsInStateSpecialJS?market=canada&siteId=canada&language=en&state=&_locationType=Search.LocationTypes.Dealer&searchMode=proximity&searchKey=52.088165%7C-106.6498956&address=S7J%205L6,%20ca&maxproximity=10000&maxnumtries=&maxresults=1000"
    res = get_data(ca_link)
    if res:
        for r in res:
            data.append(r)

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
