import csv
from concurrent import futures
from sgrequests import SgRequests
from sgzip.static import static_coordinate_list, SearchableCountries


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


def get_data(coord):
    rows = []
    lat, lng = coord
    locator_domain = "https://www.citybbq.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/json; charset=UTF-8",
        "Origin": "https://03919locator.wave2.io",
        "Connection": "keep-alive",
        "Referer": "https://03919locator.wave2.io/",
        "TE": "Trailers",
    }

    data = (
        '{"Latitude":"'
        + lat
        + '","Longitude":"'
        + lng
        + '","Address":"","City":"","State":"","Zipcode":"","Country":"","Action":"initload","ActionOverwrite":"","Filters":"FCS,FIATM,ATMSF,ATMDP,ESC,"}'
    )

    session = SgRequests()

    r = session.post(
        "https://locationapi.wave2.io/api/client/getlocations",
        headers=headers,
        data=data,
    )
    js = r.json()["Features"]
    for j in js:
        a = j.get("Properties")
        page_url = "https://www.acuonline.org/home/resources/locations"

        street_address = "".join(a.get("Address")).capitalize() or "<MISSING>"
        city = a.get("City") or "<MISSING>"
        state = a.get("State") or "<MISSING>"
        postal = a.get("Postalcode") or "<MISSING>"
        country_code = a.get("Country") or "US"
        store_number = "<MISSING>"
        phone = a.get("Phone") or "<MISSING>"
        latitude = a.get("Latitude") or "<MISSING>"
        longitude = a.get("Longitude") or "<MISSING>"
        location_type = j.get("LocationFeatures").get("LocationType")
        location_name = a.get("LocationName") + " " + location_type
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        tmp = []
        for d in days:
            day = d
            try:
                opens = a.get(f"{d}Open")
                closes = a.get(f"{d}Close")
                line = f"{day} {opens} - {closes}"
                if opens == closes:
                    line = "<MISSING>"
            except:
                line = "<MISSING>"
            tmp.append(line)
        hours_of_operation = "; ".join(tmp)
        if hours_of_operation.count("<MISSING>") == 7:
            hours_of_operation = "<MISSING>"
        hours_of_operation = hours_of_operation.replace("Closed -", "Closed").strip()
        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "Closed"
        if hours_of_operation.find("<MISSING>") != -1:
            hours_of_operation = "<MISSING>"

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
    coords = static_coordinate_list(radius=100, country_code=SearchableCountries.USA)

    with futures.ThreadPoolExecutor(max_workers=7) as executor:
        future_to_url = {executor.submit(get_data, coord): coord for coord in coords}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                _id = row[2]
                straddr = row[3]
                if _id not in s and straddr not in s:
                    s.add(_id)
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
