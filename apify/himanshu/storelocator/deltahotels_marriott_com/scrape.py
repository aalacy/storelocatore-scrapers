import csv
from sgrequests import SgRequests

session = SgRequests()
import json
from bs4 import BeautifulSoup

base_url = "https://delta-hotels.marriott.com/"


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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
    url = "https://pacsys.marriott.com/data/marriott_properties_DE_en-US.json"
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
    }
    address = []
    request = session.get(url, headers=headers)
    soup = BeautifulSoup(request.text, "lxml")
    data = soup.text
    store_list = json.loads(data)
    data_8 = store_list["regions"]
    for i in data_8:
        for j in i["region_countries"]:
            for k in j["country_states"]:
                for h in k["state_cities"]:
                    for g in h["city_properties"]:
                        if "USA" in (g["country_name"]):
                            zipp = g["postal_code"]
                            location_name = g["name"]
                            street_address = g["address"]
                            city = g["city"]
                            state = g["state_name"]
                            country_code = g["country_name"]
                            phone = g["phone"]
                            latitude = g["latitude"]
                            longitude = g["longitude"]
                            key = g["marsha_code"]
                            page_url = "https://www.marriott.com/hotels/travel/" + str(
                                key
                            )
                            output = []
                            output.append(base_url if base_url else "<MISSING>")
                            output.append(
                                location_name if location_name else "<MISSING>"
                            )
                            output.append(
                                street_address if street_address else "<MISSING>"
                            )
                            output.append(city if city else "<MISSING>")
                            output.append(state if state else "<MISSING>")
                            output.append(zipp if zipp else "<MISSING>")
                            output.append(country_code if country_code else "<MISSING>")
                            output.append("<MISSING>")
                            output.append(phone if phone else "<MISSING>")
                            output.append("Delta Hotels by Marriott")
                            output.append(latitude if latitude else "<MISSING>")
                            output.append(longitude if longitude else "<MISSING>")
                            output.append("<MISSING>")
                            output.append(page_url if page_url else "<MISSING>")
                            if output[2] in address:
                                continue
                            address.append(output[2])
                            yield output
    for i1 in data_8:
        for j1 in i1["region_countries"]:
            for k1 in j1["country_states"]:
                for h1 in k1["state_cities"]:
                    for g1 in h1["city_properties"]:
                        if "CA" in (g1["country_code"]):
                            zipp = g1["postal_code"]
                            location_name = g1["name"]
                            street_address = g1["address"]
                            city = g1["city"]
                            state = g1["state_name"]
                            country_code = g1["country_name"]
                            phone = g1["phone"]
                            latitude = g1["latitude"]
                            longitude = g1["longitude"]
                            key = g1["marsha_code"]
                            page_url = "https://www.marriott.com/hotels/travel/" + str(
                                key
                            )
                            output = []
                            output.append(base_url if base_url else "<MISSING>")
                            output.append(
                                location_name if location_name else "<MISSING>"
                            )
                            output.append(
                                street_address if street_address else "<MISSING>"
                            )
                            output.append(city if city else "<MISSING>")
                            output.append(state if state else "<MISSING>")
                            output.append(zipp if zipp else "<MISSING>")
                            output.append(country_code if country_code else "<MISSING>")
                            output.append("<MISSING>")
                            output.append(phone if phone else "<MISSING>")
                            output.append("Delta Hotels by Marriott")
                            output.append(latitude if latitude else "<MISSING>")
                            output.append(longitude if longitude else "<MISSING>")
                            output.append("<MISSING>")
                            output.append(page_url if page_url else "<MISSING>")
                            if output[2] in address:
                                continue
                            address.append(output[2])
                            yield output
    for i2 in data_8:
        for j2 in i2["region_countries"]:
            for k2 in j2["country_states"]:
                for h2 in k2["state_cities"]:
                    for g2 in h2["city_properties"]:
                        if "GB" in (g2["country_code"]):
                            zipp = g2["postal_code"]
                            location_name = g2["name"]
                            street_address = g2["address"]
                            city = g2["city"]
                            state = g2["state_name"]
                            country_code = g2["country_name"]
                            phone = g2["phone"]
                            latitude = g2["latitude"]
                            longitude = g2["longitude"]
                            key = g2["marsha_code"]
                            page_url = "https://www.marriott.com/hotels/travel/" + str(
                                key
                            )
                            output = []
                            output.append(base_url if base_url else "<MISSING>")
                            output.append(
                                location_name if location_name else "<MISSING>"
                            )
                            output.append(
                                street_address if street_address else "<MISSING>"
                            )
                            output.append(city if city else "<MISSING>")
                            output.append(state if state else "<MISSING>")
                            output.append(zipp if zipp else "<MISSING>")
                            output.append(country_code if country_code else "<MISSING>")
                            output.append("<MISSING>")
                            output.append(phone if phone else "<MISSING>")
                            output.append("Delta Hotels by Marriott")
                            output.append(latitude if latitude else "<MISSING>")
                            output.append(longitude if longitude else "<MISSING>")
                            output.append("<MISSING>")
                            output.append(page_url if page_url else "<MISSING>")
                            if output[2] in address:
                                continue
                            address.append(output[2])
                            yield output


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
