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


def addy_ext(addy):
    address = addy.split(",")
    city = address[0]
    state_zip = address[1].strip().split(" ")
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code


def fetch_data():
    # Your scraper here
    locator_domain = "https://www.chichispizza.com/"
    ext = "locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(locator_domain + ext, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    hours = " ".join(list(base.find(id="WRchTxt2-hrv").stripped_strings))
    try:
        hours = hours.split("*")[-1].strip()
    except:
        pass

    main = base.find(id="Containervtsik")
    divs = main.find_all(class_="_1Z_nJ")

    all_store_data = []
    switch = True
    for div in divs:
        if switch:
            location_name = div.text.strip()
            switch = False
        else:
            content = div.text.split("\n")

            if len(content) == 3:
                street_address = content[0]
                city, state, zip_code = addy_ext(content[1])
                phone_number = content[2]
            else:
                street_address = content[1]
                city, state, zip_code = addy_ext(content[2])
                phone_number = content[3]

            lat = "<MISSING>"
            longit = "<MISSING>"
            country_code = "US"
            store_number = "<MISSING>"
            location_type = "<MISSING>"

            store_data = [
                locator_domain,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone_number,
                location_type,
                lat,
                longit,
                hours,
                locator_domain + ext,
            ]
            all_store_data.append(store_data)
            switch = True
    return all_store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
