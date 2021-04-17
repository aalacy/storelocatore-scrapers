import csv

from lxml import html
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
    locator_domain = "https://impark.com/"
    api_url = "https://blenz.com/wp-admin/admin-ajax.php"

    data = {
        "action": "store_wpress_listener",
        "method": "display_map",
        "page_number": "1",
        "lat": "49.264173",
        "lng": "-123.0804993,16",
        "nb_display": "100",
    }

    session = SgRequests()
    r = session.post(api_url, data=data)
    js = r.json()["locations"]

    for j in js:
        line = j.get("address")
        line = line.split(",")
        line = list(filter(None, [l.strip() for l in line]))
        if "Canada" in line:
            line.pop(line.index("Canada"))

        street_address = line.pop(0)
        if "street" in line[0].lower():
            street_address += f", {line.pop(0)}"

        city = line.pop(0).replace(".", "")
        if line:
            line = line[0]
            if " " in city and len(city.split()[-1]) == 2:
                state = city.split()[-1]
                city = city.replace(state, "").strip()
            else:
                state = line.split()[0]

            if len(state) != 2:
                postal = state
                state = "<MISSING>"
            else:
                postal = line.replace(state, "").replace("Canada", "").strip()
        else:
            postal = city.split("Canada")[-1].strip()
            state = city.split("Canada")[0].strip().split()[-1].strip()
            city = city.split(state)[0].strip()
        country_code = "CA"
        store_number = j.get("id") or "<MISSING>"
        page_url = f"https://blenz.com/locations/?store_id={store_number}"
        location_name = j.get("name")
        phone = j.get("tel") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"

        if "closed" in location_name.lower():
            hours_of_operation = "Temporarily Closed"
        else:
            _tmp = []
            source = j.get("description") or "<html></html>"
            tree = html.fromstring(source)
            hours = tree.xpath("./text()")
            hours = list(filter(None, [h.strip() for h in hours]))
            for h in hours:
                if (":" not in h and "closed" not in h.lower()) or "covid" in h.lower():
                    continue
                _tmp.append(h.replace(">", "").strip())

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
