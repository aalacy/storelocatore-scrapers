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
    locator_domain = "https://locations.myhspstores.com/"
    api_url = "https://locations.myhspstores.com/wp-admin/admin-ajax.php"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://locations.myhspstores.com/?location=4698-4644%20Cheeney%20St,%20Santa%20Clara,%20CA%2095054,%20%D0%A1%D0%A8%D0%90&radius=100",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://locations.myhspstores.com",
        "Proxy-Authorization": "Basic YWNjZXNzX3Rva2VuOmc3NzExNnBzajZqbGZhaHM5dHJwMDdocm0ydTlxNGVzM3BhaGNrYm9oY2kzOGEzMWtpdQ==",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "Trailers",
    }

    data = {"action": "get_all_stores", "lat": "", "lng": ""}
    r = session.post(api_url, headers=headers, data=data)
    js = r.json()
    for j in js.values():
        location_name = "".join(j.get("na"))
        if (
            location_name.find("Pharmacy") == -1
            and location_name.find("Hi-School") == -1
        ):
            continue
        street_address = j.get("st")
        phone = j.get("te") or "<MISSING>"
        city = "".join(j.get("ct")).strip()
        if city.find(",") != -1:
            city = city.split(",")[0]
        state = "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("lng")
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        page_url = "".join(j.get("gu"))
        postal = j.get("zp") or "<MISSING>"

        if state == "<MISSING>":
            session = SgRequests()
            r = session.get(page_url)
            tree = html.fromstring(r.text)
            state = (
                "".join(
                    tree.xpath(
                        '//div[@class="section-share-summary-subtitle"][2]/text()'
                    )
                )
                or "<MISSING>"
            )
            if state != "<MISSING>":
                state = state.split(",")[1].split()[0]
            if phone == "<MISSING>":
                phone = (
                    "".join(tree.xpath('//span[@role="link"]/text()')) or "<MISSING>"
                )

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
