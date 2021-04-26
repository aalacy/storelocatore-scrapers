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
    locator_domain = "https://rabba.com"
    api_url = "https://apps.elfsight.com/p/boot/?w=a704bb89-331e-48f2-8f03-98e35b08e2bc"
    session = SgRequests()

    r = session.get(api_url)
    js = r.json()

    for j in js["data"]["widgets"]["a704bb89-331e-48f2-8f03-98e35b08e2bc"]["data"][
        "settings"
    ]["markers"]:
        ad = "".join(j.get("infoAddress"))
        street_address = ad.split(",")[0]
        city = ad.split(",")[1].strip()
        postal = " ".join(ad.split(",")[2].split()[1:]).strip()
        state = ad.split(",")[2].split()[0].strip()
        country_code = "CA"
        store_number = "<MISSING>"
        location_name = j.get("infoTitle")
        phone = j.get("infoPhone")
        ll = "".join(j.get("coordinates"))
        latitude = ll.split(",")[0]
        longitude = ll.split(",")[1]
        location_type = "<MISSING>"
        hours_of_operation = j.get("infoWorkingHours")
        page_url = "https://rabba.com/locations/"

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
