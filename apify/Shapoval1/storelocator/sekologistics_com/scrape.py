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

    locator_domain = "https://www.sekologistics.com"
    api_url = "https://www.sekologistics.com/data/locations/?culture=en-US&date=20210702t151856z"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["regions"]
    for j in js:
        for c in j["countries"]:
            country_code = c.get("name")
            for o in c["offices"]:
                page_url = f"https://www.sekologistics.com{o.get('url')}"
                location_name = o.get("name")
                location_type = "<MISSING>"
                street_address = f"{o.get('address1')} {o.get('address2')}".strip()
                state = o.get("officeCounty") or "<MISSING>"
                postal = "".join(o.get("officePostcode")) or "<MISSING>"
                postal = postal.replace("500038, T.S.", "500038")
                if postal.find("BRU 1931") != -1:
                    state = postal.split()[0].strip()
                    postal = postal.replace("BRU", "").strip()
                if postal.find("TX, 75063") != -1:
                    state = postal.split(",")[0].strip()
                    postal = postal.replace("TX,", "").strip()
                if postal.find("PA, 16801") != -1:
                    state = postal.split(",")[0].strip()
                    postal = postal.replace("PA,", "").strip()
                if postal.find("CA, 92626") != -1:
                    state = postal.split(",")[0].strip()
                    postal = postal.replace("CA,", "").strip()
                if postal.find("ME, 04101") != -1:
                    state = postal.split(",")[0].strip()
                    postal = postal.replace("ME,", "").strip()
                if postal.find("CO, 80216") != -1:
                    state = postal.split(",")[0].strip()
                    postal = postal.replace("CO,", "").strip()
                if postal.find("CA, 91708") != -1:
                    state = postal.split(",")[0].strip()
                    postal = postal.replace("CA,", "").strip()
                if postal.find("NSW, 2020") != -1:
                    state = postal.split(",")[0].strip()
                    postal = postal.replace("NSW,", "").strip()
                if postal.find("NSW 2020") != -1:
                    state = postal.split()[0].strip()
                    postal = postal.replace("NSW", "").strip()
                if postal == "0":
                    postal = "<MISSING>"
                city = o.get("officeCity")
                store_number = o.get("id")
                latitude = "".join(o.get("officeLocation").get("position")).split(",")[
                    0
                ]
                longitude = "".join(o.get("officeLocation").get("position")).split(",")[
                    1
                ]
                phone = "".join(o.get("officePhone")).replace("ext. 104", "").strip()
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
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
