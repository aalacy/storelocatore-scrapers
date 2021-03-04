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


def get_data():
    rows = []
    locator_domain = "https://www.nespresso.com"
    api_url = "https://www.nespresso.com/storelocator/app/find_poi-v4.php?country=US"
    session = SgRequests()
    r = session.get(api_url)
    js = r.json()
    for j in js:

        street_address = j.get("point_of_interest").get("address").get("address_line")
        city = j.get("point_of_interest").get("address").get("city").get("name")
        state = "<MISSING>"
        postal = j.get("point_of_interest").get("address").get("postal_code")
        country_code = "US"
        store_number = "<MISSING>"
        location_name = (
            j.get("point_of_interest")
            .get("address")
            .get("name")
            .get("company_name_type")
            .get("name")
            .get("name")
        )
        phone = j.get("point_of_interest").get("phone") or "<MISSING>"
        page_url = "https://www.nespresso.com/us/en/storeLocator"
        latitude = j.get("position").get("latitude")
        longitude = j.get("position").get("longitude")
        location_type = j.get("point_of_interest").get("type")
        hours = j.get("point_of_interest").get("opening_hours_text").get("text")
        hours_of_operation = html.fromstring(hours)
        hours_of_operation = (
            " ".join(hours_of_operation.xpath("//text()[1] | //text()[2]"))
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation.find("Bloomingdales") != -1:
            hours_of_operation = hours_of_operation.split("Bloomingdales")[0].strip()
        if hours_of_operation.find("Located") != -1:
            hours_of_operation = hours_of_operation.split("Located")[0].strip()
        if hours_of_operation.find("Sur") != -1:
            hours_of_operation = hours_of_operation.split("Sur")[0].strip()
        if hours_of_operation.find("Macy's") != -1:
            hours_of_operation = hours_of_operation.split("Macy's")[0].strip()
        if hours_of_operation.find("*Doorside") != -1:
            hours_of_operation = hours_of_operation.split("*Doorside")[0].strip()
        if hours_of_operation.find("Mall") != -1:
            hours_of_operation = hours_of_operation.split("Mall")[0].strip()
        if hours_of_operation.find("Americana") != -1:
            hours_of_operation = hours_of_operation.split("Americana")[0].strip()

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

        rows.append(row)
    return rows


def scrape():
    data = get_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
