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
    locator_domain = "http://pressecafe.com/fr/"
    api_url = "http://pressecafe.com/fr/stores/?ajax=1&lat=45.5086699&lng=-73.5539925&dist=50000"
    session = SgRequests()

    r = session.get(api_url)
    js = r.json()

    for j in js["stores"]:
        a = j.get("fields")
        street_address = a.get("address")
        city = a.get("city")
        postal = a.get("postal_code")
        state = a.get("province")
        country_code = a.get("country")
        store_number = "<MISSING>"
        location_name = a.get("name")
        phone = "".join(a.get("phone"))
        if phone.find("poste") != -1:
            phone = phone.split("poste")[0].strip()
        latitude = a.get("lat")
        longitude = a.get("lng")
        location_type = "<MISSING>"
        hours_of_operation = f"Monday {a.get('monday_hours')} Tuesday {a.get('tuesday_hours')} Wednesday {a.get('wednesday_hours')} Thursday {a.get('thursday_hours')} Friday {a.get('friday_hours')} Saturday {a.get('saturday_hours')} Sunday {a.get('sunday_hours')}"
        page_url = "http://pressecafe.com/fr/stores/"

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
