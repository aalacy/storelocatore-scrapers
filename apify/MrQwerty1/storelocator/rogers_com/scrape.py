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
    s = set()
    url = "https://www.rogers.com/"

    session = SgRequests()
    headers = {"Accept": "application/json"}

    for i in range(0, 100000, 10):
        r = session.get(
            f"https://www.rogers.com/stores/index.html?l=en&offset={i}", headers=headers
        )
        js = r.json()["response"]["entities"]
        for jj in js:
            j = jj.get("profile")
            a = j.get("address")
            locator_domain = url
            street_address = (
                f"{a.get('line1')} {a.get('line2') or ''}".strip() or "<MISSING>"
            )
            city = a.get("city") or "<MISSING>"
            location_name = j.get("name")
            state = a.get("region") or "<MISSING>"
            postal = a.get("postalCode") or "<MISSING>"
            country_code = a.get("countryCode") or "<MISSING>"
            store_number = "<MISSING>"
            page_url = (
                j.get("websiteUrl")
                if j.get("websiteUrl")
                else j.get("c_pagesURL") or "<MISSING>"
            )
            if page_url == "<MISSING>" or page_url in s:
                continue

            s.add(page_url)
            phone = j.get("mainPhone", {}).get("display") or "<MISSING>"
            latitude = j.get("yextDisplayCoordinate", {}).get("lat") or "<MISSING>"
            longitude = j.get("yextDisplayCoordinate", {}).get("long") or "<MISSING>"
            location_type = "<MISSING>"

            hours = j.get("hours", {}).get("normalHours", [])
            _tmp = []
            for h in hours:
                day = h.get("day")
                if not h.get("isClosed"):
                    interval = h.get("intervals")
                    start = str(interval[0].get("start"))
                    if len(start) == 3:
                        start = f"0{start}"
                    end = str(interval[0].get("end"))
                    line = f"{day[:3].capitalize()}: {start[:2]}:{start[2:]} - {end[:2]}:{end[2:]}"
                else:
                    line = f"{day[:3].capitalize()}: Closed"
                _tmp.append(line)

            hours_of_operation = ";".join(_tmp) or "<MISSING>"
            if hours_of_operation.count("Closed") == 7:
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
            out.append(row)
        if len(js) < 10:
            break

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
