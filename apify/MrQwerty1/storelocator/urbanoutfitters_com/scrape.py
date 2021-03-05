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
    url = "https://www.urbanoutfitters.com/stores/"
    api_url = (
        "https://www.urbanoutfitters.com/api/misl/v1/stores/search?&country=US,"
        "CA&urbn_key=937e0cfc7d4749d6bb1ad0ac64fce4d5&brandId=51|01"
    )

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["results"]

    for j in js:
        locator_domain = url
        try:
            location_name = j["addresses"]["marketing"]["name"]
        except KeyError:
            location_name = j.get("storeName")
        if (
            location_name.lower().find("closed") != -1
            or location_name.lower().find("soon") != -1
        ):
            continue
        street_address = (
            j.get("addresses", {}).get("marketing", {}).get("addressLineOne")
            or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        store_number = j.get("storeNumber") or "<MISSING>"
        page_url = f'https://www.urbanoutfitters.com/stores/{j.get("slug")}'
        phone = j.get("storePhoneNumber") or "<MISSING>"
        if phone.find("?") != -1:
            phone = "<MISSING>"
        country_code = j["country"]
        latitude = j.get("loc")[1] if j.get("loc") else "<MISSING>"
        longitude = j.get("loc")[0] if j.get("loc") else "<MISSING>"
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
        hours = j.get("hours")
        for d, h in zip(days, hours.values()):
            start = h.get("open").lower()
            close = h.get("close").lower()
            if start == "closed" or close == "closed":
                _tmp.append(f"{d} CLOSED")
            else:
                _tmp.append(f"{d} {start} - {close}")

        hours_of_operation = ";".join(_tmp)
        if hours_of_operation.count("CLOSED") == 7:
            continue

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
