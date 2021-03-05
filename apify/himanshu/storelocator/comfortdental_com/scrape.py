import csv

from bs4 import BeautifulSoup

from sgrequests import SgRequests

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
    base_url = "https://comfortdental.com"
    url = "https://comfortdental.com/wp-admin/admin-ajax.php"
    data = "action=locatornonce"

    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9,pt;q=0.8",
        "content-length": "206",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://comfortdental.com",
        "referer": "https://comfortdental.com/find-a-dentist/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    locatornonce = session.post(url, headers=headers, data=data).json()["nonce"]
    payload = (
        "action=locate&address=80261&formatted_address=Denver%2C+CO+80261%2C+USA&locatorNonce="
        + str(locatornonce)
        + "&distance=10000000000&latitude=39.73999999999999&longitude=-104.98&unit=miles&geolocation=false&allow_empty_address=false"
    )
    json_data = session.post(url, headers=headers, data=payload).json()

    for data in json_data["results"]:
        location_name = data["title"]
        if "closed" in location_name.lower():
            continue
        store_number = data["id"]
        lat = data["latitude"]
        lng = data["longitude"]
        page_url = data["permalink"]
        soup = list(BeautifulSoup(data["output"], "lxml").stripped_strings)
        street_address = soup[-5]
        city = soup[-4].split(",")[0]
        state = soup[-4].split(",")[1].split()[0]
        zipp = soup[-4].split(",")[1].split()[1].replace("87214", "87124")
        phone = soup[-3]

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36",
        }
        location_soup = BeautifulSoup(
            session.get(page_url, headers=headers).content, "lxml"
        )
        try:
            hours = " ".join(list(location_soup.find(id="hoursTable").stripped_strings))
            if "Coming Soon" in hours:
                continue
        except:
            hours = "<MISSING>"

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
        store.append("Comfort Dental")
        store.append(lat)
        store.append(lng)
        store.append(hours)
        store.append(page_url)

        store = [str(x).strip() if x else "<MISSING>" for x in store]

        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
