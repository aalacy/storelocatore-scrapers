import codecs
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


def get_urls():
    urls = [
        "https://co-opcreditunions.org/wp-content/themes/coop019901/inc/locator/locator-csv.php?loctype=AS&country=UK&Submit=Search%22"
    ]

    postals = static_zipcode_list(radius=10, country_code=SearchableCountries.USA)
    for postal in postals:
        urls.append(
            f"https://co-opcreditunions.org/wp-content/themes/coop019901/inc/locator/locator-csv.php?loctype=AS&zip={postal}&maxradius=10&country=&Submit=Search%22"
        )

    return urls


def get_data(url):
    rows = []
    slug = url.split("?")[-1].replace("%22", "")
    page_url = f"https://co-opcreditunions.org/locator/search-results/?{slug}"
    locator_domain = "https://www.co-opfs.org/Shared-Branches-ATMs"

    session = SgRequests()
    r = session.get(url)
    text = r.iter_lines()
    js = csv.DictReader(codecs.iterdecode(text, "utf-8"))

    for j in js:
        location_name = j.get("Name")
        street_address = j.get("Address") or "<MISSING>"
        city = j.get("City") or "<MISSING>"
        state = j.get("State") or "<MISSING>"
        if "," in state:
            state = state.replace(",", "").strip() or "<MISSING>"
        postal = j.get("Zip") or "<MISSING>"
        if "-" in postal:
            postal = postal.split("-")[0].strip()
        if len(postal) == 4:
            postal = f"0{postal}"

        country = j.get("Country") or ""
        if "STATES" in country:
            country_code = "US"
        else:
            country_code = "GB"
        store_number = "<MISSING>"
        phone = j.get("Phone") or "<MISSING>"
        if "/>" in phone:
            phone = phone.split("/>")[-1].strip()

        latitude = j.get("Latitude") or "<MISSING>"
        longitude = j.get("Longitude") or "<MISSING>"
        if not j.get("AcceptsDeposit"):
            location_type = "Shared Branch"
        else:
            location_type = "ATM"

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
        for day in days:
            part = day[:3]
            start = j.get(f"Hours{part}Open")
            end = j.get(f"Hours{part}Close")
            if not start:
                continue
            if "Closed" in start:
                _tmp.append(f"{day}: Closed")
            else:
                _tmp.append(f"{day}: {start} - {end}")

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
        rows.append(row)

    return rows


def fetch_data():
    out = []
    s = set()
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                t = tuple(row[2:11])
                if t not in s:
                    s.add(t)
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
