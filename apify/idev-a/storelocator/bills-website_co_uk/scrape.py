import csv
import json
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
    base_url = "https://www.bills-website.co.uk"
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "cookie": "_gcl_au=1.1.2056240407.1610815778; AtreemoUniqueID_cookie=e5ec4d8d-1593-bd7f-7171-36dbb248a706-1610815779957; _fbp=fb.2.1610815782941.1688925043; _ga=GA1.3.1870464924.1610815787; _gid=GA1.3.1203183535.1610815787; _gat_UA-41730338-6=1; XSRF-TOKEN=eyJpdiI6InN2RjlWUFlndlFYcXh0d3dOODlheGc9PSIsInZhbHVlIjoiZkgxSlhJUUhZMEpVcjNNc1FxdUg4NFpoT0EwWkZ6bVRCTHREZklVQVA1WG1QRVhUUzZsaDM3bDJydmVzS2YxciIsIm1hYyI6ImE1MzA0MWUyOGVmOTIyOGY2MzJjNmMzOTI1OTYwZTU2ZTI1ZWM2NjczYzdmYjc4OTJkYjU3MDdkYWZiNDM0ZmYifQ%3D%3D; bills_session=eyJpdiI6InltcXh1dGdaSG83c05XUEZYSUkySEE9PSIsInZhbHVlIjoiTUdIOWtuRjhscDhUbmdGTm1RR0NES3N6RlZQVlRcL2VWdkZWaEgxNTRMSWNLb3FOT3hcL1J6aFV4a0l1Mzh3RU84IiwibWFjIjoiY2E0MDY0YWM4YWY4ZmRkZjI5NGVkZDRjM2M5YjIyZmFhN2M5OTQ4OGFlOTQ1YWM0NzU4ZGRkZDU5M2E0YWExMSJ9",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    }
    res = session.get("https://www.bills-website.co.uk/restaurants", headers=headers)
    regions = json.loads(
        res.text.split(':components="')[1]
        .split('"')[0]
        .replace("&quot;", '"')
        .replace("\\/", "/")
    )
    regions = regions[0]["value"]["regions"]
    data = []
    for region in regions:
        location_list = region["locations"]
        for x in location_list:
            try:
                location = location_list[x]
            except:
                location = x
            location_name = location["title"].replace("&#039;", "'")

            page_url = base_url + location["url"]
            phone = location["meta"][1]["content"]
            if "closed" in location["meta"][0]["content"]:
                zip = "<MISSING>"
                city = "<MISSING>"
                street_address = "<MISSING>"
            else:
                address = location["meta"][0]["content"].split(", ")
                city_zip = address.pop()
                if len(city_zip.split(" ")) == 2:
                    zip = city_zip
                    city = address.pop().replace("&#039;", "'")
                else:
                    zip = " ".join(city_zip.split(" ")[-2:])
                    city = " ".join(city_zip.split(" ")[:-2]).replace("&#039;", "'")
                street_address = " ".join(address).replace("&#039;", "'")
            if location_name == "Sevenoaks":
                address = location["meta"][0]["content"].split(", ")
                zip = address.pop()
                city = "<MISSING>"
                street_address = " ".join(address).replace("&#039;", "'")
            res1 = session.get(page_url)
            hours = json.loads(
                res1.text.split(':components="')[1]
                .split('"')[0]
                .replace("&quot;", '"')
                .replace("\\/", "/")
            )[0]["value"]["hours"][0]["times"]
            hours_of_operation = ""
            for hour in hours:
                hours_of_operation += hour["title"] + " " + hour["content"] + " "
            hours_of_operation = hours_of_operation.replace("&amp;amp;", "&")
            if "temporarily closed" in res1.text:
                hours_of_operation = "Temporarily closed " + hours_of_operation
            country_code = "UK"
            store_number = "<MISSING>"
            location_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            state = "<MISSING>"

            data.append(
                [
                    base_url,
                    page_url,
                    location_name,
                    street_address,
                    city,
                    state,
                    zip,
                    country_code,
                    store_number,
                    '="' + phone + '"',
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


if __name__ == "__main__":
    scrape()
