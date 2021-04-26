import csv
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
    locator_domain = "https://valentinos.com"
    api_url = "https://valentinos.com/wp-json/wp/v2/locations/?per_page=100"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()
    for j in js:
        ad = j.get("post_meta_fields")
        street_address = ad.get("address_street_address")[0]
        city = ad.get("address_city")[0]
        postal = ad.get("address_zip")[0]
        state = ad.get("address_state")[0]
        phone = ad.get("phone")[0]
        country_code = "US"
        store_number = "<MISSING>"
        location_name = (
            "".join(j.get("title").get("rendered"))
            .replace("&#8211;", "-")
            .replace("&#8217;", "`")
        )
        try:
            latitude = ad.get("maps_location").get("lat")
            longitude = ad.get("maps_location").get("lng")
        except AttributeError:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        location_type = j.get("type")
        page_url = "https://valentinos.com/locations/"
        hours_of_operation = (
            "".join(ad.get("hours"))
            .replace("\n", "")
            .replace("\t", "")
            .replace("</br>", " ")
            .replace("\r", "")
            .replace("<br>", " ")
        )
        if hours_of_operation.find("Buffet, Carryout, Delivery") != -1:
            hours_of_operation = (
                hours_of_operation.split("Buffet, Carryout, Delivery")[1]
                .split(".")[0]
                .strip()
            )
        if hours_of_operation.find("Buffet") != -1:
            hours_of_operation = hours_of_operation.split("Buffet")[0].strip()
        if hours_of_operation.find("Dine-In") != -1:
            hours_of_operation = hours_of_operation.split("Dine-In")[0].strip()
        if hours_of_operation.find("Student Union hours") != -1:
            hours_of_operation = "<MISSING>"
        if hours_of_operation.find("Dining") != -1:
            hours_of_operation = hours_of_operation.split("Dining")[0].strip()
        if hours_of_operation.find("TEMPORARILY CLOSED") != -1:
            hours_of_operation = "Temporarily closed"
        if hours_of_operation.find("Temporarily closed") != -1:
            hours_of_operation = "Temporarily closed"
        if hours_of_operation.find("Party") != -1:
            hours_of_operation = hours_of_operation.split("Party")[0].strip()
        hours_of_operation = (
            hours_of_operation.replace("Carryout & Delivery", "")
            .replace("Carryout", "")
            .strip()
        )

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
