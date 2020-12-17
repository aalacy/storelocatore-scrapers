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
    locator_domain = "https://www.tcfbank.com/"
    api_url = "https://dotcom-location-api.dotcom-prod-ase.p.azurewebsites.net/api/mergelocations/getbygeofilterquery?latitude=44.8739807&longitude=-93.3352547&distance=5000&count=5000"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["Results"]

    for s in js:
        j = s.get("BankLocation")
        a = j.get("Address")
        location_type = j.get("LocationType") or "<MISSING>"
        if location_type == "ATM":
            continue
        street_address = a.get("Street") or "<MISSING>"
        city = a.get("City") or "<MISSING>"
        state = a.get("State") or "<MISSING>"
        postal = a.get("PostalCode") or "<MISSING>"
        country_code = "US"
        store_number = j.get("Id") or "<MISSING>"
        page_url = f'https://www.tcfbank.com/locations/details/{j.get("FormttedUrlForDetailsPage")}'
        location_name = j.get("Name") or "<MISSING>"
        phone = "<MISSING>"
        loc = j.get("Coordinates")
        latitude = loc[0]
        longitude = loc[1]
        hours_of_operation = j.get("HoursLobby") or "<MISSING>"

        if page_url.find("temporarily-closed") != -1:
            hours_of_operation = "Temporarily Closed"

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
