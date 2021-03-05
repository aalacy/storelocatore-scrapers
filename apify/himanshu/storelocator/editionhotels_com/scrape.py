import csv
from bs4 import BeautifulSoup
import json
import time
from sgrequests import SgRequests

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


def request_wrapper(url, method, headers, data=None):
    request_counter = 0
    if method == "get":
        while True:
            try:
                r = session.get(url, headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    elif method == "post":
        while True:
            try:
                if data:
                    r = session.post(url, headers=headers, data=data)
                else:
                    r = session.post(url, headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    else:
        return None


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }
    base_url = "https://www.editionhotels.com/"
    url_list = ["miaeb", "nyceb", "nycte", "laxeb", "loneb"]
    for j in url_list:
        location_url = "https://www.marriott.com/hotels/travel/" + str(j)
        r = request_wrapper(location_url, "get", headers=headers)
        soup = BeautifulSoup(r.text, "lxml")
        data = soup.find_all("script", {"type": "application/ld+json"})
        mp = str(data).split('application/ld+json">')[1].split("</script")[0]
        json_data = json.loads(mp)
        location_name = json_data["@graph"][-1]["name"]
        street_address = json_data["@graph"][-1]["address"]["streetAddress"]
        city = json_data["@graph"][-1]["address"]["addressLocality"]
        zipp = json_data["@graph"][-1]["address"]["postalCode"]
        country_code = json_data["@graph"][-1]["address"]["addressCountry"]
        phone = json_data["@graph"][-1]["telephone"]
        state = json_data["@graph"][-1]["address"]["addressRegion"]
        latitude = json_data["@graph"][-1]["geo"]["latitude"]
        longitude = json_data["@graph"][-1]["geo"]["longitude"]
        store = []
        store.append(base_url if base_url else "<MISSING>")
        store.append(location_name if location_name else "<MISSING>")
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append(country_code if country_code else "<MISSING>")
        store.append(j.upper())
        store.append(phone if phone else "<MISSING>")
        store.append("EDITION Hotels")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append("<MISSING>")
        store.append(location_url if location_url else "<MISSING>")
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
