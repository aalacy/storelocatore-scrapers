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

    locator_domain = "https://www.fcbanking.com"
    api_url = "https://www.fcbanking.com/umbraco/surface/LocationSurface/SearchAllLocationsJSON?slat=40.500848995731744&slon=-80.56009&searchType=2%2C0&query=&sne_lat=45.324727869599215&sne_lon=-72.375275546875&ssw_lat=35.303467299573455&ssw_lon=-88.744904453125&_=1624125606907"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    s = set()
    for j in js:

        slug = j.get("url")
        page_url = f"{locator_domain}{slug}"
        if not slug:
            page_url = "https://www.fcbanking.com/branch-locations/"
        location_name = j.get("Name") or "<MISSING>"
        location_type = "ATM"
        street_address = j.get("StreetAddress") or "<MISSING>"
        state = j.get("StateCode") or "<MISSING>"
        postal = j.get("PostalCode") or "<MISSING>"
        country_code = "USA"
        city = j.get("City") or "<MISSING>"
        store_number = j.get("ID") or "<MISSING>"
        latitude = j.get("Latitude") or "<MISSING>"
        longitude = j.get("Longitude") or "<MISSING>"
        phone = j.get("Phone") or "<MISSING>"
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        tmp = []
        for d in days:
            times = j.get(f"BranchLobbyHours_{d}")
            if times is None:
                continue
            line = f"{d} {times}"
            tmp.append(line)
        hours_of_operation = ";".join(tmp) or "<MISSING>"

        line = (street_address, location_name)
        if line in s:
            continue
        s.add(line)

        session = SgRequests()
        r = session.get(
            "https://www.fcbanking.com/umbraco/surface/LocationSurface/GetAllBranchLocationsJSON?_=1624124908409",
            headers=headers,
        )
        js = r.json()
        for j in js:
            street_addresss = "".join(j.get("StreetAddress")).split()[:2]
            street_addresss = " ".join(street_addresss)

            if street_address.find(f"{street_addresss}") != -1:
                phone = j.get("Phone")
                store_number = j.get("ID")
                days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                tmp = []
                for d in days:
                    times = j.get(f"BranchLobbyHours_{d}")
                    if times is None:
                        continue
                    line = f"{d} {times}"
                    tmp.append(line)
                hours_of_operation = ";".join(tmp) or "<MISSING>"
                slug = j.get("url")
                page_url = f"{locator_domain}{slug}"

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
