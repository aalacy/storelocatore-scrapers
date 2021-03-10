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
    rows = []
    session = SgRequests()
    locator_domain = "https://www.bloomingdales.com"

    r = session.get("https://locations.bloomingdales.com/index.json")
    js = r.json()["keys"]
    for j in js:
        slug = j.get("url")
        j = j.get("loc")

        location_name = j.get("name")
        page_url = j.get("website").get("url") or "<MISSING>"
        if page_url == "<MISSING>":
            page_url = f"https://locations.bloomingdales.com/{slug}"

        street_address = (
            f"{j.get('address1')} {j.get('address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("postalCode") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        store_number = j.get("corporateCode") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        isoutlet = j.get("customByName").get("Outlet")
        isrest = j.get("customByName").get("Restaurant")
        _types = []
        if isoutlet:
            _types.append("Outlet")
        else:
            _types.append("Retail")
        if isrest:
            _types.append("Restaurant")

        location_type = ", ".join(_types)
        days = j.get("hours", {}).get("days") or []

        _tmp = []
        for d in days:
            day = d.get("day")[:3].capitalize()
            try:
                interval = d.get("intervals")[0]
                start = str(interval.get("start"))
                end = str(interval.get("end"))

                if len(start) == 3:
                    start = f"0{start}"

                if len(end) == 3:
                    end = f"0{end}"

                line = f"{day}  {start[:2]}:{start[2:]} - {end[:2]}:{end[2:]}"
            except IndexError:
                line = f"{day}  Closed"

            _tmp.append(line)

        hours_of_operation = ";".join(_tmp) or "<MISSING>"
        isclosed = j.get("closed")
        if isclosed:
            hours_of_operation = "Closed"

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

        rows.append(row)

    return rows


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
