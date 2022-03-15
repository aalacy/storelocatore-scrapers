import base64
import csv
from concurrent import futures
from sgrequests import SgRequests
from sgzip.static import static_zipcode_list, SearchableCountries


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


def get_data(_zip):
    rows = []

    locator_domain = "https://www.onestop.co.uk"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    zip_bytes = _zip.encode("ascii")
    base64_bytes = base64.b64encode(zip_bytes)
    base64_zip = base64_bytes.decode("ascii")

    data = {
        "action": "findstockists",
        "searchfor": str(base64_zip),
    }
    session = SgRequests()
    r = session.post(
        "https://www.onestop.co.uk/wp-admin/admin-ajax.php", headers=headers, data=data
    )
    js = r.json()
    try:
        if "locations" in js["message"]:
            for loc in js["message"]["locations"]:

                location_name = loc.get("location").get("name") or "<MISSING>"
                store_number = "<MISSING>"
                country_code = "GB"
                state = "<MISSING>"
                street_address = (
                    loc.get("location").get("address").get("details").get("lines")[0]
                )
                if (
                    len(loc.get("location").get("address").get("details").get("lines"))
                    == 2
                ):
                    street_address = (
                        street_address
                        + " "
                        + loc.get("location")
                        .get("address")
                        .get("details")
                        .get("lines")[1]
                    )
                city = (
                    loc.get("location").get("address").get("details").get("postTown")
                    or "<MISSING>"
                )

                postal = (
                    loc.get("location").get("address").get("details").get("postcode")
                    or "<MISSING>"
                )
                phone = (
                    loc.get("location").get("contact").get("phoneNumbers").get("main")
                    or "<MISSING>"
                )
                latitude = (
                    loc.get("location").get("coordinates").get("latitude")
                    or "<MISSING>"
                )
                longitude = (
                    loc.get("location").get("coordinates").get("longitude")
                    or "<MISSING>"
                )
                location_type = loc.get("location").get("types")[0] or "<MISSING>"
                try:
                    monday_hrs = f"Monday: {loc.get('location').get('openingHours').get('standard').get('monday').get('intervals')[0].get('start')} - {loc.get('location').get('openingHours').get('standard').get('monday').get('intervals')[0].get('end')}"
                    tuesday_hrs = f"Tuesday: {loc.get('location').get('openingHours').get('standard').get('tuesday').get('intervals')[0].get('start')} - {loc.get('location').get('openingHours').get('standard').get('tuesday').get('intervals')[0].get('end')}"
                    wednesday_hrs = f"Wednesday: {loc.get('location').get('openingHours').get('standard').get('wednesday').get('intervals')[0].get('start')} - {loc.get('location').get('openingHours').get('standard').get('wednesday').get('intervals')[0].get('end')}"
                    thursday_hrs = f"Thursday: {loc.get('location').get('openingHours').get('standard').get('thursday').get('intervals')[0].get('start')} - {loc.get('location').get('openingHours').get('standard').get('thursday').get('intervals')[0].get('end')}"
                    friday_hrs = f"Friday: {loc.get('location').get('openingHours').get('standard').get('friday').get('intervals')[0].get('start')} - {loc.get('location').get('openingHours').get('standard').get('friday').get('intervals')[0].get('end')}"
                    saturday_hrs = f"Saturday: {loc.get('location').get('openingHours').get('standard').get('saturday').get('intervals')[0].get('start')} - {loc.get('location').get('openingHours').get('standard').get('saturday').get('intervals')[0].get('end')}"
                    try:
                        sunday_hrs = f"Sunday: {loc.get('location').get('openingHours').get('standard').get('sunday').get('intervals')[0].get('start')} - {loc.get('location').get('openingHours').get('standard').get('sunday').get('intervals')[0].get('end')}"
                    except:
                        sunday_hrs = "Sunday Closed"
                except:
                    monday_hrs = "<MISSING>"
                    tuesday_hrs = "<MISSING>"
                    wednesday_hrs = "<MISSING>"
                    thursday_hrs = "<MISSING>"
                    friday_hrs = "<MISSING>"
                    saturday_hrs = "<MISSING>"
                    sunday_hrs = "<MISSING>"

                hours_of_operation = (
                    monday_hrs
                    + " "
                    + tuesday_hrs
                    + " "
                    + wednesday_hrs
                    + " "
                    + thursday_hrs
                    + " "
                    + friday_hrs
                    + " "
                    + saturday_hrs
                    + " "
                    + sunday_hrs
                    or "<MISSING>"
                )
                if hours_of_operation.count("<MISSING>") == 7:
                    hours_of_operation = "<MISSING>"

                page_url = f"https://www.onestop.co.uk/store/?store={loc.get('location').get('id')}"

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
                rows.append(row)
    except:
        return
    return rows


def fetch_data():
    out = []
    s = set()
    postals = static_zipcode_list(radius=20, country_code=SearchableCountries.BRITAIN)

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {
            executor.submit(get_data, postal): postal for postal in postals
        }
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            try:
                for row in rows:
                    _id = row[1]
                    if _id not in s:
                        s.add(_id)
                        out.append(row)
            except TypeError:
                continue

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
