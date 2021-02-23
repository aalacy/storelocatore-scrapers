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


def get_token():
    session = SgRequests()
    data = {"app_key": "foodtown", "referrer": "https://www.foodtown.com/"}
    r = session.post("https://api.freshop.com/2/sessions/create", data=data)

    return r.json()["token"]


def fetch_data():
    out = []
    locator_domain = "https://www.foodtown.com/"
    token = get_token()
    api_url = f"https://api.freshop.com/1/stores?app_key=foodtown&has_address=true&is_selectable=true&limit=-1&token={token}"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["items"]

    for j in js:
        adr0 = j.get("address_0") or ""
        adr1 = j.get("address_1") or ""
        adr2 = j.get("address_2") or ""
        if adr0.lower().find("shopping") != -1:
            adr0 = ""
        if adr2.lower().find("shopping") != -1:
            adr2 = ""

        street_address = f"{adr0} {adr1} {adr2}".strip()
        city = j.get("city") or "<MISSING>"
        if city.find(",") != -1:
            city = city.split(",")[-1].strip()
        state = j.get("state") or "<MISSING>"
        postal = j.get("postal_code") or "<MISSING>"
        country_code = "US"
        store_number = j.get("number") or "<MISSING>"
        page_url = j.get("url") or "<MISSING>"
        location_name = j.get("name")
        phone = j.get("phone_md") or "<MISSING>"
        if phone.find("\n") != -1:
            phone = phone.split("\n")[0].replace("Store:", "").strip()
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"

        hours = j.get("hours", "") or j.get("hours_md")
        if hours.find("Store") != -1:
            hours = hours.split("\n")[0].replace("Store:", "").strip()

        if hours.find("\n") != -1:
            hours = ";".join(list(filter(None, [h.strip() for h in hours.split("\n")])))

        hours_of_operation = hours or "<MISSING>"

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
