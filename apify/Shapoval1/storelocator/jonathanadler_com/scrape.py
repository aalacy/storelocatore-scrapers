import csv
from lxml import html
from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

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

        for row in data:
            writer.writerow(row)


def fetch_data():
    out = []

    locator_domain = "https://jonathanadler.com/"
    api_url = "https://stores.boldapps.net/front-end/get_surrounding_stores.php?shop=jonathanadler-com.myshopify.com&latitude=40.735165&longitude=-74.000536&max_distance=10000&limit=100"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js["stores"]:

        page_url = "https://jonathanadler.com/apps/store-locator"
        location_name = j.get("name")
        location_type = "<MISSING>"
        street_address = f"{j.get('address')} {j.get('address2')}".replace(
            "None", ""
        ).strip()
        phone = j.get("phone")
        state = j.get("prov_state")
        postal = j.get("postal_zip")
        country_code = "".join(j.get("country"))
        if country_code.find("GB") != -1:
            continue
        city = j.get("city")
        store_number = "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours = j.get("hours")
        hours = html.fromstring(hours)
        hours_of_operation = (
            "".join(hours.xpath("//*/text()"))
            .replace("\n", "")
            .replace("\r", " ")
            .strip()
        )
        if hours_of_operation.find("The health") != -1:
            hours_of_operation = hours_of_operation.split("The health")[0].strip()
        if hours_of_operation.find("Reduced") != -1:
            hours_of_operation = hours_of_operation.split("Reduced")[0].strip()
        if hours_of_operation.find("Holiday") != -1:
            hours_of_operation = hours_of_operation.split("Holiday")[0].strip()
        if hours_of_operation.find("Available") != -1:
            hours_of_operation = hours_of_operation.split("Available")[0].strip()
        if hours_of_operation.find("Open") != -1:
            hours_of_operation = hours_of_operation.split("Open")[0].strip()
        hours_of_operation = hours_of_operation.replace("Hours:", "").strip()

        row = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            postal,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
