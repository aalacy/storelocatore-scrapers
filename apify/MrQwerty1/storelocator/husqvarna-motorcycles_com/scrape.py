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
    locator_domain = "https://www.husqvarna-motorcycles.com/"
    api_url = "https://www.husqvarna-motorcycles.com/content/websites/husqvarna-motorcycles-com/north-america/us/en/dealer-search/jcr:content/root/responsivegrid_1_col/dealersearch.dealers.json?latitude=33.0218117&longitude=-97.12516989999999&country=&qualification=&distance=5000"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["data"]

    for j in js:
        street_address = j.get("street") or "<MISSING>"
        city = j.get("town") or "<MISSING>"
        state = j.get("region") or "<MISSING>"
        postal = j.get("postcode") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        page_url = "<MISSING>"
        location_name = j.get("name")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("geoCodeLatitude") or "<MISSING>"
        longitude = j.get("geoCodeLongitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = j.get("openingHour") or "<MISSING>"
        hours_of_operation = " ".join(
            hours_of_operation.replace("\n\n", ";")
            .replace("\n", ";")
            .replace("<br/>", ";")
            .replace("STORE HOURS;", "")
            .replace("; ;", ";")
            .replace(";;", ";")
            .split()
        )
        if ");" in hours_of_operation:
            hours_of_operation = hours_of_operation.split(");")[-1].strip()

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
