import csv
from sgrequests import SgRequests
import json

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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    }

    base_url = "https://www.benspretzels.com/"
    json_url = "https://app.locatedmap.com/initwidget/?instanceId=b8d5e841-7e84-4b86-af79-9341996bc5ef&compId=comp-izqi4x5u&viewMode=json&styleId=style-jr7yn9r0"
    r = session.get(json_url, headers=headers)
    json_data = json.loads(r.json()["mapSettings"])[0]["fields"]["unpublishedLocations"]

    for dt in json_data:
        location_name = dt["name"]
        temp_add = dt["formatted_address"].replace(", USA", "").split(",")
        if len(temp_add) == 4:
            zipp = temp_add[3]
            state = temp_add[2]
            city = temp_add[1]
            street_address = temp_add[0]

        elif len(temp_add) == 3:
            zipp = temp_add[-1].split(" ")[2]
            state = temp_add[-1].split(" ")[1]
            city = temp_add[-2]
            street_address = " ".join(str(n) for n in temp_add[:-2])
        elif len(temp_add) == 2:
            temp_st = temp_add[0].split(" ")
            street_address = " ".join(temp_st[:-1])
            city = temp_st[-1]
            state = temp_add[1].split(" ")[-2]
            zipp = temp_add[1].split(" ")[-1]
        elif len(temp_add) == 1:
            temp_add = dt["formatted_address"].replace(", USA", "").replace("  ", " ")
            temp_add = temp_add.split(" ")
            zipp = temp_add[-1]
            state = temp_add[-2]
            city = temp_add[-3]
            street_address = " ".join(str(n) for n in temp_add[:-3])

        if dt["tel"] == "":
            phone = "<MISSING>"
        else:
            phone = dt["tel"]
        location_type = "Ben's Pretzels"
        latitude = dt["latitude"]
        longitude = dt["longitude"]

        if dt["opening_hours"] == "":
            hours_of_operation = "<MISSING>"
        else:
            hours_of_operation = (
                dt["opening_hours"]
                .replace(
                    "Ben's Soft Pretzels is located inside Spartan Stadium at Michigan State University",
                    "<MISSING>",
                )
                .replace(
                    "Ben's Soft Pretzels at Ohio Stadium at The Ohio State University",
                    "<MISSING>",
                )
            )
        if location_name == "Ben's Soft Pretzels- Terre Haute Walmart":
            street_address = street_address.replace("Terre", "")
            city = "Terre Haute"

        city = city.lstrip().replace(",", "")
        state = state.lstrip().replace(",", "")
        zipp = zipp.lstrip().replace(",", "")
        hours_of_operation = hours_of_operation.replace("–", "-")
        data.append(
            [
                base_url,
                "https://www.benspretzels.com/locations",
                location_name,
                street_address,
                city,
                state,
                zipp,
                "US",
                "<MISSING>",
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
