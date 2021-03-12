import csv
from sgrequests import SgRequests

session = SgRequests()
import json
from bs4 import BeautifulSoup

base_url = "https://ac-hotels.marriott.com/"


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
    url = "https://pacsys.marriott.com/data/marriott_properties_AR_en-US.json"
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
    for region in data_8:
        if region["region_id"] == "north.america":
            for country in region["region_countries"]:
                for stat in country["country_states"]:
                    for cty in stat["state_cities"]:
                        for loc in cty["city_properties"]:
                            zipp = loc["postal_code"]
                            location_name = loc["name"]
                            temp_street_address = loc["address"]
                            street_address = "".join(
                                char for char in temp_street_address if ord(char) < 128
                            )
                            city = loc["city"]
                            state = loc["state_name"]
                            country_code = loc["country_name"]
                            phone = loc["phone"]
                            latitude = loc["latitude"]
                            longitude = loc["longitude"]
                            key = loc["marsha_code"]
                            page_url = "https://www.marriott.com/hotels/travel/" + str(
                                key
                            )
                            output = []
                            output.append(base_url if base_url else "<MISSING>")
                            output.append(
                                location_name if location_name else "<MISSING>"
                            )
                            output.append(
                                street_address.replace("é", "e")
                                if street_address
                                else "<MISSING>"
                            )
                            output.append(city if city else "<MISSING>")
                            output.append(state if state else "<MISSING>")
                            output.append(zipp if zipp else "<MISSING>")
                            output.append(country_code if country_code else "<MISSING>")
                            output.append("<MISSING>")
                            output.append(phone if phone else "<MISSING>")
                            output.append("AC Hotel Marriott")
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
