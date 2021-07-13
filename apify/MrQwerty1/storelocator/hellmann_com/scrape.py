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
    locator_domain = "https://www.hellmann.com/"
    api_url = "https://www.hellmann.com/en/api/location"
    page_url = "https://www.hellmann.com/en/united-states/contact"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:
        try:
            street_address = (
                j["field_address"][0]["value"].replace(".", "") or "<MISSING>"
            )
        except:
            street_address = "<MISSING>"

        try:
            city = j["field_city"][0]["value"].replace(".", "") or "<MISSING>"
        except:
            city = "<MISSING>"
        state = "<MISSING>"
        try:
            postal = j["field_zipcode"][0]["value"].replace(".", "") or "<MISSING>"
        except:
            postal = "<MISSING>"
        country_code = j.get("country_iso_code") or "<MISSING>"
        if country_code == "US" and " " in postal or "PO" in postal:
            postal = postal.split()[-1]
        if "," in postal:
            pp = postal.split()
            for p in pp:
                if p[0].isdigit():
                    postal = p
                    break

        postal = postal.replace("Hubei", "<MISSING>").replace(" Lisboa", "")
        if postal == "<MISSING>" and city[0].isdigit():
            postal = city.split()[0]
            city = city.replace(city, "").strip()

        if city.endswith(","):
            city = city[:-1]

        if "2690-379" in street_address:
            street_address = street_address.replace("2690-379 ", "")
            postal = "2690-379"

        try:
            store_number = j["path"][0]["pid"]
        except:
            store_number = "<MISSING>"
        location_name = j["title"][0]["value"].strip()
        try:
            phone = j["field_phone"][0]["value"]
        except:
            phone = "<MISSING>"
        try:
            latitude = j["field_latitude"][0]["value"]
        except:
            latitude = "<MISSING>"
        try:
            longitude = j["field_longitude"][0]["value"]
        except:
            longitude = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"

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
