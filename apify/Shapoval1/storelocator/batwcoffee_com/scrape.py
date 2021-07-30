import csv
from lxml import html
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

    locator_domain = "https://batwcoffee.com"
    api_url = "https://cdn.shopify.com/s/files/1/2358/5201/t/9/assets/sca.storelocatordata.json?v=1616792042&origLat=49.302687&origLng=-123.033209&origAddress=1462%20Columbia%20St%2C%20North%20Vancouver%2C%20BC%20V7J%201A2%2C%20%D0%9A%D0%B0%D0%BD%D0%B0%D0%B4%D0%B0&formattedAddress=&boundsNorthEast=&boundsSouthWest="

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js:
        ad = "".join(j.get("address")).replace("Get directions", "").strip()
        street_address = ad.split(",")[0].strip()
        city = ad.split(",")[1].strip()
        postal = " ".join(ad.split(",")[2].split()[1:]).strip()
        state = ad.split(",")[2].split()[0].strip()
        if ad.find("506") != -1 or ad.find("10510") != -1:
            postal = ad.split(",")[-1].strip()
        phone = j.get("phone") or "<MISSING>"
        country_code = "CA"
        store_number = "<MISSING>"
        location_name = "".join(j.get("name")).strip()
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"

        page_url = j.get("web")
        if ad.find("506") != -1:
            page_url = (
                "https://batwcoffee.com/pages/bean-around-the-world-5th-chesterfield"
            )
        if ad.find("10510") != -1:
            page_url = "https://batwcoffee.com/pages/bean-around-the-world-edmonton"

        hours = j.get("schedule")
        hours = html.fromstring(hours)
        hours_of_operation = hours.xpath("//*/text()")
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = " ".join(hours_of_operation)

        if ad.find("2528") != -1:
            hours_of_operation = hours_of_operation + " " + "11:00 PM"
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
