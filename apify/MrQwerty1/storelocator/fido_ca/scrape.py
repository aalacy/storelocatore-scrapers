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
    locator_domain = "https://www.fido.ca/"

    session = SgRequests()
    headers = {"Accept": "application/json"}

    for i in range(0, 100000, 50):
        r = session.get(
            f"https://www.fido.ca/stores/index.html?q=&offset={i}", headers=headers
        )
        js = r.json()["response"]["entities"]

        for jj in js:
            j = jj.get("profile")
            a = j.get("address")
            page_url = j.get("c_pagesURL") or "<MISSING>"
            store_number = "<MISSING>"
            street_address = (
                f'{a.get("line1")} {a.get("line2") or ""}'.strip().replace("\n", ", ")
                or "<MISSING>"
            )
            city = a.get("city") or "<MISSING>"
            location_name = j.get("name")
            state = a.get("region") or "<MISSING>"
            postal = a.get("postalCode") or "<MISSING>"
            country_code = a.get("countryCode") or "<MISSING>"
            phone = j.get("mainPhone", {}).get("display") or "<MISSING>"
            latitude = j.get("yextDisplayCoordinate", {}).get("lat") or "<MISSING>"
            longitude = j.get("yextDisplayCoordinate", {}).get("long") or "<MISSING>"
            location_type = j.get("c_storeType") or "<MISSING>"
            if location_type != "Main Store":
                continue

            hours = j.get("hours", {}).get("normalHours", [])
            _tmp = []
            for h in hours:
                day = h.get("day")
                if not h.get("isClosed"):
                    interval = h.get("intervals")
                    start = str(interval[0].get("start"))
                    if len(start) == 3:
                        start = f"0{start}"
                    if len(start) == 1:
                        start = "1200"
                    end = str(interval[0].get("end"))
                    line = f"{day[:3].capitalize()}: {start[:2]}:{start[2:]} - {end[:2]}:{end[2:]}"
                else:
                    line = f"{day[:3].capitalize()}: Closed"
                _tmp.append(line)

            hours_of_operation = ";".join(_tmp) or "<MISSING>"
            if hours_of_operation.count("Closed") == 7:
                hours_of_operation = "Closed"
            if "Coming Soon" in location_name or j.get("c_comingSoon"):
                hours_of_operation = "Coming Soon"

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

            check = (street_address, city, state, postal)
            if check not in s:
                s.add(check)
                out.append(row)

        if len(js) < 50:
            break

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
