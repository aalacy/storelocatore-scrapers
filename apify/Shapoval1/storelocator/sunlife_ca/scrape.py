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

    locator_domain = "https://www.sunlife.ca"
    page_url = (
        "https://www.sunlife.ca/services/AdvisorMatchHandler/AdvisorMatchResults.ashx"
    )

    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    data = {
        "dist": "2500",
        "gend": "",
        "des": "",
        "e": "y",
        "loc": "0",
        "pc": "M8W 1J4",
        "lng": "-79.5340868",
        "lat": "43.5925628",
        "prov": "ON",
        "city": "Toronto",
        "lang": "en",
        "locale": "en_CA",
        "num": "1000",
    }

    r = session.post(page_url, headers=headers, data=data)
    js = r.json()

    for j in js["AdvisorResultList"]:
        a = j.get("FC")
        page_url = "https://www.sunlife.ca/en/find-an-advisor/#"
        street_address = "".join(a.get("Street"))
        if street_address.find("<br><br>") != -1:
            street_address = street_address.split("<br><br>")[1].strip()
        city = a.get("City")
        state = j.get("Prov")
        postal = a.get("PC")
        store_number = "<MISSING>"
        location_name = j.get("Name")
        latitude = a.get("Lat")
        longitude = a.get("Lat")
        country_code = "CA"
        location_type = "<MISSING>"
        phone = a.get("Phone")
        hours_of_operation = j.get("WorkHours") or "<MISSING>"
        tmp = []
        if hours_of_operation != "<MISSING>":
            for h in hours_of_operation:
                days = h.get("WeekDay")
                opens = h.get("OpenHour")
                closes = h.get("CloseHour")
                line = f"{days} {opens}-{closes}"
                tmp.append(line)
            hours_of_operation = ";".join(tmp)

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
