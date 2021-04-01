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
    locator_domain = "https://www.vets4pets.com/"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
        "Accept": "*/*",
        "Referer": "https://www.vets4pets.com/find-a-practice/",
    }

    for i in range(1, 10):
        r = session.get(
            f"https://api.woosmap.com/stores/search?key=woos-85314341-5e66-3ddf-bb9a-43b1ce46dbdc&lat=51.50732&lng=-0.12764746&max_distance=500000&stores_by_page=300&page={i}",
            headers=headers,
        )
        js = r.json()["features"]

        for j in js:
            g = j.get("geometry")
            j = j.get("properties")
            c = j.get("contact")
            a = j.get("address")
            street_address = (
                ", ".join(a.get("lines")).replace("Inside Pets at Home,", "").strip()
                or "<MISSING>"
            )
            city = a.get("city") or "<INACCESSIBLE>"
            if city.find("(") != -1:
                city = "<INACCESSIBLE>"
            state = "<MISSING>"
            postal = a.get("zipcode") or "<MISSING>"
            if postal.find("(") != -1:
                postal = postal.split("(")[0].strip()
            country_code = a.get("country_code") or "<MISSING>"
            store_number = j.get("store_id") or "<MISSING>"
            page_url = c.get("website") or "<MISSING>"
            location_name = j.get("name")
            phone = c.get("phone") or "<MISSING>"
            longitude, latitude = g.get("coordinates") or ["<MISSING>", "<MISSING>"]
            location_type = "<MISSING>"

            _tmp = []
            days = [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
            hours = j.get("opening_hours").get("usual")
            for k, v in hours.items():
                day = days[int(k) - 1]
                start = v[0].get("start")
                close = v[0].get("end")
                _tmp.append(f"{day}: {start} - {close}")

            hours_of_operation = ";".join(_tmp) or "<MISSING>"
            if page_url in s:
                continue

            s.add(page_url)
            row = [
                locator_domain,
                page_url,
                location_name,
                street_address,
                city,
                state,
                postal.strip(),
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
            out.append(row)

        if len(js) < 300:
            break

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
