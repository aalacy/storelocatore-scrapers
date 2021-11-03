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

    locator_domain = "https://www.pasticceriamarchesi.com"
    api_url = "https://www.pasticceriamarchesi.com/en/shops.getShopStores.json"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)

    js = r.json().values()
    for j in js:
        for a in j:

            page_url = "https://www.pasticceriamarchesi.com/en/shops.html"
            location_name = a.get("short_name")
            location_type = a.get("type")
            street_address = a.get("address")[0]
            ad = "".join(a.get("address")[1]).replace("London,", "London")
            phone = a.get("phone")
            state = "<MISSING>"
            postal = ad.split()[0].strip()
            city = ad.split()[1].strip()
            country_code = a.get("countryGroup")
            store_number = "<MISSING>"
            hours_of_operation = (
                "".join(a.get("hours")).replace("/", "").replace("\r\n", "").strip()
            )
            latitude = a.get("map").get("lat")
            longitude = a.get("map").get("lng")

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
