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


def fetch_data():

    data = []
    found = []
    base_link = "https://www.porsche.com/all/dealer2/GetLocationsWebService.asmx/GetGlobalDealers?market=canada&siteId=canada&language=en&searchKey=52.088165%7C-106.6498956"

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find("listoflocations").find_all("location")

    locator_domain = "porsche.com"
    for item in items:
        location_name = item.find("name").text.strip()
        try:
            street_address = item.find("street").text.replace("Côte", "Cote")
        except:
            continue
        city = item.find("city").text.strip()

        if street_address + city in found:
            continue
        found.append(street_address + city)

        try:
            state = item.find("statecode").text.upper()
        except:
            state = "<MISSING>"
        try:
            zip_code = item.find("postcode").text
            if len(zip_code) == 4:
                zip_code = "0" + zip_code
        except:
            zip_code = "<MISSING>"
        store_number = item.find("id").text
        if store_number in found:
            continue
        found.append(store_number)

        location_type = "<MISSING>"
        latitude = item.find("coordinates").find("lat").text
        longitude = item.find("coordinates").find("lng").text.replace("E+07", "")
        try:
            phone = item.find("phone").text
        except:
            phone = "<MISSING>"
        hours_of_operation = "<MISSING>"

        try:
            country_code = item.find("countrycode").text.upper()
        except:
            country_code = item.find("market").text.upper()
        if "LATIN" in country_code or "MIDDLE" in country_code:
            country_code = state
            state = "<MISSING>"
        try:
            link = item.find("url1").text
        except:
            link = "<MISSING>"
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
