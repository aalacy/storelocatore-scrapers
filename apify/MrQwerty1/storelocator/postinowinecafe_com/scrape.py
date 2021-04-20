import codecs
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
    locator_domain = "https://www.postinowinecafe.com/"
    api_url = "https://c4d5x4f7.stackpathcdn.com/wp-content/themes/wp-brigade-theme/img/locations20181008c.csv"

    session = SgRequests()
    r = session.get(api_url)
    text = r.iter_lines()
    js = csv.DictReader(codecs.iterdecode(text, "utf-8"))

    for j in js:
        location_name = j.get("Fcilty_nam")
        street_address = j.get("Street_add") or "<MISSING>"
        city = j.get("Locality") or "<MISSING>"
        if "," in city:
            city = city.split(",")[0].strip()

        state = "<MISSING>"
        if j.get("AZ") == "YES":
            state = "AZ"
        if j.get("CO") == "YES":
            state = "CO"
        if j.get("TX") == "YES":
            state = "TX"

        postal = j.get("Postcode") or "<MISSING>"
        if " " in postal:
            postal = postal.split()[-1]
        country_code = "US"
        store_number = "<MISSING>"
        page_url = j.get("Fcilty_typ_2") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("Ycoord") or "<MISSING>"
        longitude = j.get("Xcoord") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = j.get("Hrs_of_bus") or "<MISSING>"

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
