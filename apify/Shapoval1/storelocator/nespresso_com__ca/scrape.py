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
    api_url = "https://www.nespresso.com/storelocator/app/find_poi-v4.php?country=CA"
    session = SgRequests()
    r = session.get(api_url)
    js = r.json()
    for j in js:

        street_address = (
            "".join(j.get("point_of_interest").get("address").get("address_line"))
            .replace("<br/>", "")
            .replace("<br>", "")
        )
        city = j.get("point_of_interest").get("address").get("city").get("name")
        state = "<MISSING>"
        postal = j.get("point_of_interest").get("address").get("postal_code")
        country_code = "CA"
        store_number = "<MISSING>"
        location_name = "".join(
            j.get("point_of_interest")
            .get("address")
            .get("name")
            .get("company_name_type")
            .get("name")
            .get("name")
        ).capitalize()
        phone = j.get("point_of_interest").get("phone") or "<MISSING>"
        page_url = "https://www.nespresso.com/ca/en/StoreLocator"
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
        hoursfor = html.fromstring(hours)
        hoursfor = (
            " ".join(hoursfor.xpath("//text()[3] | //text()[4]"))
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation.find("Paiements") != -1:
            hours_of_operation = hours_of_operation.split("Paiements")[0].strip()
        if hours_of_operation.find("Civic Holiday Aug 3:") != -1:
            hours_of_operation = hours_of_operation.split("   ")[1].strip()
        if hours_of_operation.find("CLOSED") != -1:
            hours_of_operation = "Closed"
        if hours_of_operation.find("Payments") != -1:
            hours_of_operation = hours_of_operation.split("Payments")[0].strip()
        if street_address.find("Centre2002") != -1:
            hours_of_operation = hoursfor

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
