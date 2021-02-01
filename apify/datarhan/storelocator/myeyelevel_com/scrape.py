import re
import csv
import json

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
    # Your scraper here
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "myeyelevel.com"
    start_url = "https://www.myeyelevel.com/US/customer/getCenterList.do"
    country_codes = ["0015", "0014"]
    for code in country_codes:
        formdata = {
            "pageName": "findCenter",
            "centerLati": "",
            "searchType": "",
            "centerLongi": "",
            "surDistance": "",
            "myLocLati": "0",
            "myLocLongi": "0",
            "countryCd": code,
            "cityCd": "",
            "centerName": "",
            "listSort": "D",
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
        }

        response = session.post(start_url, data=formdata, headers=headers)
        data = json.loads(response.text)

        for poi in data:
            if poi.get("homeurl"):
                store_url = "https://" + poi["homeurl"]
            else:
                store_url = "<MISSING>"
            location_name = poi["centerName"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["address"]
            print(street_address)
            if len(street_address.split(",")) > 1:
                if "Unit" in street_address.split(",")[1]:
                    street_address = ", ".join(street_address.split(",")[:2])
                elif "Suit" in street_address.split(",")[1]:
                    street_address = ", ".join(street_address.split(",")[:2])

                else:
                    street_address = street_address.split(",")[0]
            street_address = street_address if street_address else "<MISSING>"
            if poi.get("pCity"):
                if len(poi["pCity"].split(",")) > 1:
                    city = poi["pCity"].split(",")[0]
                    state = poi["pCity"].split(",")[-1]
                else:
                    city = poi["pCity"]
                    if len(city.split()) > 1:
                        if len(city.split()[-1].strip()) == 2:
                            city = city.split()[0]
                            state = poi["pCity"].split()[-1]
                    else:
                        state = "<MISSING>"
            else:
                if len(poi["address"].split(",")) > 1:
                    city = poi["address"].split(",")[-2].strip()
                    if "#" in city:
                        if len(city) > 7:
                            city = re.findall(r"#\d+ (.+)", city)
                            city = city[0] if city else poi["address"].split()[-3]
                        else:
                            city = poi["address"].split(",")[-1].strip().split()[0]
                    if len(city.split()) > 2:
                        city = "<MISSING>"
                    if ("Unit" and "Suit") in city:
                        city = " ".join(poi["address"].split(",")[-1].split()[:-2])
                    state = " ".join(poi["address"].split(",")[-1].split()[1:])
                    if not state:
                        state = poi["address"].split(",")[-1]
                    if len(state) > 2:
                        if len(poi["address"].split(",")[-1].split()) > 1:
                            state = poi["address"].split(",")[-1].split()[-2]
                            if len(state) > 2:
                                state = "<MISSING>"
                        else:
                            state = "<MISSING>"
                else:
                    city = poi["address"].split()[-3]
                    if city == "Jose":
                        city = "San Jose"
                    state = poi["address"].split()[-2]
            city = city.capitalize()
            zip_code = poi.get("zipcode")
            if not zip_code:
                zip_code = poi["address"].split()[-1]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = ""
            country_code = country_code if country_code else "<MISSING>"
            store_number = poi["centerNo"]
            store_number = store_number if store_number else "<MISSING>"
            phone = poi.get("phone")
            phone = phone if phone else "<MISSING>"
            location_type = ""
            location_type = location_type if location_type else "<MISSING>"
            latitude = poi["locLati"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["locLongi"]
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = poi["centerOpenTime"]
            hours_of_operation = (
                hours_of_operation if hours_of_operation else "<MISSING>"
            )

            if len(city.split()) == 2:
                if len(city.split()[-1]) == 2:
                    city = city.split()[0]
                    state = city.split()[-1]

            street_address = street_address.replace(city, "")

            item = [
                DOMAIN,
                store_url,
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

            if store_number not in scraped_items:
                scraped_items.append(store_number)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
