import csv
import yaml

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
    locator_domain = "https://www.marketdistrict.com/"
    api_url = (
        "https://www.marketdistrict.com/api/sitecore/Store/FetchStoreDetails?zipcode="
    )

    session = SgRequests()
    r = session.get(api_url)
    text = r.text.replace("\t", "")
    js = yaml.load(text, Loader=yaml.Loader)["list"]

    for j in js:
        j = j.get("Location")
        a = j.get("Address")
        street_address = (
            f"{a.get('lineOne')} {a.get('lineTwo') or ''}".replace("-", "").strip()
            or "<MISSING>"
        )
        city = a.get("City") or "<MISSING>"
        state = a.get("State").get("Abbreviation") or "<MISSING>"
        postal = a.get("Zip") or "<MISSING>"
        country_code = "US"
        store_number = j.get("Id") or "<MISSING>"
        page_url = f"https://www.marketdistrict.com/store-locator/store-details?number={store_number}"
        location_name = j.get("Name")
        phone = j.get("TelephoneNumbers")[0].get("DisplayNumber") or "<MISSING>"
        loc = a.get("Coordinates")
        latitude = loc.get("Latitude") or "<MISSING>"
        longitude = loc.get("Longitude") or "<MISSING>"
        location_type = j.get("Details").get("Type").get("Name") or "<MISSING>"

        _tmp = []
        hours = j.get("HoursOfOperation") or []
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

        for h in hours:
            index = int(h.get("DayNumber")) - 1
            day = days[index]
            time = h.get("HourDisplay")
            _tmp.append(f"{day}: {time}")

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
