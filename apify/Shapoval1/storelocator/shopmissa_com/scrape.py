import csv
import json
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

    locator_domain = "https://www.shopmissa.com/"
    api_url = "https://cdn.shopify.com/s/files/1/0882/6874/t/269/assets/sca.storelocator_scripttag.js?v=1619556494&shop=shopmissa.myshopify.com"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    text = r.text.split('"locationsRaw":"')[1].split('"};')[0].replace("\\", "")
    js = json.loads(text)
    for j in js:

        page_url = j.get("web")
        location_name = j.get("name")
        location_type = "<MISSING>"
        street_address = f"{j.get('address')} {j.get('address2')}".replace(
            "None", ""
        ).strip()
        phone = j.get("phone")
        state = j.get("state") or "TX"
        postal = j.get("postal")
        country_code = j.get("country")
        city = j.get("city")
        store_number = "<MISSING>"
        try:
            hours_of_operation = "".join(j.get("schedule")).replace("r<br>", " ")
        except TypeError:
            hours_of_operation = "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("lng")

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
