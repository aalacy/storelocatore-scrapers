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

    locator_domain = "https://www.aussiegrill.com"
    api_url = "https://www.aussiegrill.com/scripts/locationData.json"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js:

        page_url = "https://www.aussiegrill.com/pickup.html"
        location_name = j.get("Name")
        location_type = "<MISSING>"
        ad = "".join(j.get("Address"))
        if not ad:
            continue
        phone = "".join(j.get("Phone")).replace("Call:", "").strip() or "<MISSING>"
        street_address = ad.split(",")[0].strip()
        state = ad.split(",")[2].split()[0].strip()
        postal = ad.split(",")[2].split()[-1].strip()
        city = ad.split(",")[1].strip()
        if ad.count(",") == 3:
            street_address = ad.split(",")[0].strip() + " " + ad.split(",")[1].strip()
            state = ad.split(",")[3].split()[0].strip()
            postal = ad.split(",")[3].split()[-1].strip()
            city = ad.split(",")[2].strip()
        country_code = "US"

        store_number = "<MISSING>"
        text = "".join(j.get("DirectionsURL"))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
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
