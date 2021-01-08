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
    locator_domain = "https://brownsshoefitcompany.com/"
    api_url = "https://brownsshoefitco.locally.com/stores/conversion_data?has_data=true&company_id=12247&inline=1&only_retailer_id=12247&only_store_id=false"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["markers"]

    for j in js:
        location_name = j.get("name") or "<MISSING>"
        street_address = j.get("address") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        page_url = f'https://stores.brownsshoefitcompany.com/{j.get("slug")}'
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        for d in days:
            part = d[:3]
            start = str(j.get(f"{part}_time_open"))
            close = str(j.get(f"{part}_time_close"))
            if start == "0":
                _tmp.append(f"{d.capitalize()}: Closed")
            else:
                if len(start) == 3:
                    start = f"0{start}"
                if start == "15":
                    start = "1200"
                start = start[:2] + ":" + start[2:]
                close = close[:2] + ":" + close[2:]
                _tmp.append(f"{d.capitalize()}: {start} - {close}")

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
