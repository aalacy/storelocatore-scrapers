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

    locator_domain = "https://eggsquis.com"
    api_url = "https://eggsquis.com/wp-content/themes/eggsquis/js/store.json"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js["features"]:
        page_url = "https://eggsquis.com"
        a = j.get("properties")
        location_name = a.get("name")
        location_type = a.get("category")
        ad = "".join(a.get("address"))

        street_address = ad.split("\n")[0].replace("\r", "")

        adr = ad.split("\n")[1]

        phone = a.get("phone") or "<MISSING>"

        state = adr.split(",")[1].replace("\r", "").strip()
        postal = ad.split("\n")[2].replace("\r", "")
        country_code = "Canada"
        city = adr.split(",")[0].replace("\r", "").strip()
        store_number = a.get("storeid")
        latitude = j.get("geometry").get("coordinates")[1]
        longitude = j.get("geometry").get("coordinates")[0]
        hours_of_operation = (
            "".join(a.get("hours"))
            .replace("\n", " ")
            .replace("Lundi", "Monday")
            .replace("Mardi", "Tuesday")
            .replace("Mercredi", "Wednesday")
            .replace("Jeudi", "Thursday")
            .replace("Vendredi", "Friday")
            .replace("Samedi", "Saturday")
            .replace("Dimanche", "Sunday")
            .replace("à", "-")
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
