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
    states = {"2": "QC"}
    locator_domain = "https://www.brunet.ca/"
    api_url = "https://www.brunet.ca/StoreLocator/StoreLocator.svc/LoadStoreInfosBH"

    session = SgRequests()
    r = session.post(api_url)
    js = r.json()["LoadStoreInfosBHResult"]

    for j in js:
        street_address = j.get("Address_e") or "<MISSING>"
        city = j.get("City") or "<MISSING>"
        state = states.get(str(j.get("State_Id"))) or "<MISSING>"
        postal = j.get("Zip_Code") or "<MISSING>"
        country_code = "CA"
        store_number = j.get("Store") or "<MISSING>"
        page_url = f"https://www.brunet.ca/en/store-locator/{store_number}/"
        location_name = j.get("Store_Name")
        phone = j.get("Front_Phone") or "<MISSING>"
        latitude = j.get("Latitude") or "<MISSING>"
        longitude = j.get("Longitude") or "<MISSING>"
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
        hours = j.get("StoreBusinessHours") or []
        for h in hours:
            index = int(h.get("Day")) - 1
            day = days[index]
            start = h.get("OpenTime")
            end = h.get("CloseTime")
            if start and end:
                _tmp.append(f"{day}: {start[:2]}:{start[2:]} - {end[:2]}:{end[2:]}")

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
