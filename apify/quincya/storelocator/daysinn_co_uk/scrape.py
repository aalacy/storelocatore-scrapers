import csv
import json

from bs4 import BeautifulSoup

from sgrequests import SgRequests

session = SgRequests()


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
    addresses = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "Connection": "keep-alive",
    }
    base_url = "https://www.wyndhamhotels.com"
    location_url1 = "https://www.wyndhamhotels.com/en-uk/days-inn/locations"
    try:
        r = session.get(location_url1, headers=headers, allow_redirects=False)
    except:
        pass
    soup = BeautifulSoup(r.text, "lxml")
    a = soup.find_all("div", {"class": "state-container"})[78].find_all(
        "li", {"class": "property"}
    )
    for b in a:
        k = b.find("a")["href"]
        location_url = base_url + k
        try:
            r1 = session.get(location_url, headers=headers, allow_redirects=False)
        except:
            pass
        soup1 = BeautifulSoup(r1.text, "lxml")
        b1 = soup1.find("script", {"type": "application/ld+json"})
        if not b1:
            continue
        b = str(b1).split('ld+json">')[1].split("</script>")[0]
        if b != [] and b is not None:
            h = json.loads(b)
            location_name = h["name"]
            street_address = (
                h["address"]["streetAddress"]
                .replace("S Wisconsin Dells Parkway South", "South")
                .strip()
            )
            latitude = h["geo"]["latitude"]
            longitude = h["geo"]["longitude"]
            city = h["address"]["addressLocality"].strip()
            if "postalCode" in h["address"]:
                zipp = h["address"]["postalCode"].strip()
            else:
                zipp = "<MISSING>"
            country_code = "UK"
            if "addressRegion" in h["address"]:
                state = h["address"]["addressRegion"].strip()
            else:
                state = "<MISSING>"
            phone = h["telephone"]
            store = []
            store.append(base_url)
            store.append(location_name if location_name else "<MISSING>")
            store.append(street_address.strip() if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append(country_code)
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append("<MISSING>")
            store.append(location_url)
            addresses.append(store[2])
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
