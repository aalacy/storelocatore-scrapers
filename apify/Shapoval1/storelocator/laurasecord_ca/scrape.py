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
    locator_domain = "https://laurasecord.ca"
    api_url = "https://spreadsheets.google.com/feeds/list/1oKjduBpXoJAExrY1RxK8bm4F8H8RVIw4pFhnAuglC-8/od6/public/values?alt=json"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js["feed"]["entry"]:

        location_name = "".join(j.get("gsx$name").get("$t")).strip()
        street_address = "".join(j.get("gsx$address").get("$t")).strip()
        city = "".join(j.get("gsx$city").get("$t")).strip()
        state = "".join(j.get("gsx$province").get("$t")).strip()
        country_code = "CA"
        postal = "".join(j.get("gsx$postalcode").get("$t")).strip()
        store_number = j.get("gsx$storenumber").get("$t")
        page_url = (
            j.get("gsx$storelink").get("$t") or "https://laurasecord.ca/find-a-store/"
        )
        latitude = j.get("gsx$lat").get("$t")
        longitude = j.get("gsx$lng").get("$t")
        location_type = j.get("gsx$type").get("$t") or "<MISSING>"
        hours_of_operation = (
            "".join(j.get("gsx$hours").get("$t"))
            .replace("\n", " ")
            .replace("Curbside PickUp Only", "")
            .replace("  ", " ")
            .replace("          ", " ")
            .strip()
        )
        phone = j.get("gsx$phone").get("$t")

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
