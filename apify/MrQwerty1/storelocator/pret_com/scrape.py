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
    locator_domain = "https://www.pret.com/"
    api_url = "https://api1.pret.com/v1/shops/"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["shops"]

    for j in js:
        a = j.get("address")
        street_address = a.get("streetNumber") or "<MISSING>"
        city = a.get("city") or "<MISSING>"
        state = a.get("region") or "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        if postal.find(" ") != -1:
            postal = postal.split()[-1]

        country_code = j.get("countryCode") or "<MISSING>"
        if country_code != "US":
            continue

        store_number = j.get("shopNumber") or "<MISSING>"
        page_url = "https://www.pret.com/en-US/shop-finder"
        location_name = j.get("name")
        phone = j.get("contact").get("phone") or "<MISSING>"
        loc = j.get("location")
        latitude = loc.get("lat") or "<MISSING>"
        longitude = loc.get("lng") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        days = [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ]
        hours = j.get("tradingHours") or []
        cnt = 0
        for h in hours:
            start = h[0]
            close = h[-1]
            day = days[cnt]
            if start != close:
                _tmp.append(f"{day}: {start} - {close}")
            else:
                _tmp.append(f"{day}: Closed")
            cnt += 1

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

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
