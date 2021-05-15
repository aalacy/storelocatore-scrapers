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

    base_link = "https://westsuburbanbank.com/locations.php"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []
    locator_domain = "westsuburbanbank.com"

    raw_hours = base.find(class_="table")
    heads = raw_hours.find_all("th")
    cols = raw_hours.find_all("tr")[1:]

    lobby_hours = ""
    for i in range(len(heads)):
        day = cols[i].td.text.strip()
        lobby = cols[i].find_all("td")[1].text.strip()
        lobby_hours = (lobby_hours + " " + day + " " + lobby).strip()
    lobby_hours = heads[1].text + " " + lobby_hours

    wsb_hours = ""
    for i in range(len(heads)):
        day = cols[i].td.text.strip()
        lobby = cols[i].find_all("td")[2].text.strip()
        wsb_hours = (wsb_hours + " " + day + " " + lobby).strip()
    wsb_hours = heads[2].text + " " + wsb_hours

    hours_of_operation = lobby_hours + " " + wsb_hours

    items = base.find(id="nav-tabContent").find_all(class_="tab-pane fade")

    for item in items:
        location_name = item.h3.text
        stores = item.find_all(class_="col-12")
        for store in stores:
            street_address = store.h5.text
            city_line = store.p.text.split(",")
            city = city_line[0].strip()
            state = city_line[-1].strip().split()[0].strip()
            zip_code = city_line[-1].strip().split()[1].strip()
            country_code = "US"
            store_number = "<MISSING>"
            phone = base.find(class_="footer-widget").find_all("a")[-1].text
            try:
                location_type = store.small.text.split(".")[0]
            except:
                location_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        data.append(
            [
                locator_domain,
                base_link,
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
