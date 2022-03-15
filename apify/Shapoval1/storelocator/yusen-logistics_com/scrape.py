import csv
from sgscrape.sgpostal import International_Parser, parse_address
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

    locator_domain = "https://www.yusen-logistics.com"
    api_url = "https://www.yusen-logistics.com/sites/all/themes/custom/ylk/json/location_en.json"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["location"]
    for j in js:
        slug = j.get("region")
        page_url = f"https://www.yusen-logistics.com/en/about-us/find-an-office#?region={slug}".replace(
            " ", "+"
        )

        location_name = "".join(j.get("title"))
        location_type = j.get("division")
        ad = "".join(j.get("address"))
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or ad
        )
        if street_address.isdigit() or street_address == "263/3":
            street_address = ad
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = j.get("country")
        city = j.get("city")
        try:
            store_number = location_name.split()[1].strip()
        except:
            store_number = "<MISSING>"
        latitude = j.get("map")[0].get("lat") or "<MISSING>"

        longitude = j.get("map")[0].get("long") or "<MISSING>"
        try:
            phone = (
                "".join(j.get("phone")[0])
                .replace("(Main Line)", "")
                .replace("(Air Export)", "")
                .replace("(Logistics)", "")
                .replace("(Yusen Logistics (Shinshu) Co., Ltd./Head office)", "")
                .replace("(Sales)", "")
                .replace("(Auto 30 Lines)", "")
                .strip()
            )
        except:
            phone = "<MISSING>"
        try:
            hours_of_operation = (
                "".join(j.get("office_hours_from")).strip()
                + " "
                + "".join(j.get("office_hours_to")).strip()
                or "<MISSING>"
            )
            hours_of_operation = hours_of_operation.replace("  ", " ").strip()
        except:
            hours_of_operation = "<MISSING>"
        if not hours_of_operation:
            hours_of_operation = "<MISSING>"
        hours_of_operation = (
            hours_of_operation.replace("800", "8:00")
            .replace("1700", "17:00")
            .replace("0900", "09:00")
            .replace("1200", "12:00")
            .replace("0830", "08:30")
            .replace("1730", "17:30")
        )

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
