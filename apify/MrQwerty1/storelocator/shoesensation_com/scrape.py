import csv
import re
import usaddress

from concurrent import futures
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


def clean_adr(text):
    try:
        tag = {
            "Recipient": "recipient",
            "AddressNumber": "address1",
            "AddressNumberPrefix": "address1",
            "AddressNumberSuffix": "address1",
            "StreetName": "address1",
            "StreetNamePreDirectional": "address1",
            "StreetNamePreModifier": "address1",
            "StreetNamePreType": "address1",
            "StreetNamePostDirectional": "address1",
            "StreetNamePostModifier": "address1",
            "StreetNamePostType": "address1",
            "CornerOf": "address1",
            "IntersectionSeparator": "address1",
            "LandmarkName": "address1",
            "USPSBoxGroupID": "address1",
            "USPSBoxGroupType": "address1",
            "USPSBoxID": "address1",
            "USPSBoxType": "address1",
            "BuildingName": "address2",
            "OccupancyType": "address2",
            "OccupancyIdentifier": "address2",
            "SubaddressIdentifier": "address2",
            "SubaddressType": "address2",
            "PlaceName": "city",
            "StateName": "state",
            "ZipCode": "postal",
        }
        a = usaddress.tag(text, tag_mapping=tag)[0]
        return f"{a.get('address1')} {a.get('address2') or ''}".replace(
            "None", ""
        ).strip()
    except:
        return text


def get_id(text):
    regex = r"\d+"
    return re.findall(regex, text)[0]


def get_hours(url):
    _tmp = []
    _id = get_id(url)
    session = SgRequests()
    r = session.get(url)
    tree = html.fromstring(r.text)
    tr = tree.xpath("//div[@class='table-responsive']//tr")
    for t in tr:
        day = "".join(t.xpath("./td[1]/text()"))
        time = "".join(t.xpath("./td[3]/text()"))
        _tmp.append(f"{day} {time}")

    hoo = ";".join(_tmp) or "<MISSING>"

    return {_id: hoo}


def fetch_data():
    out = []
    s = set()
    url = "https://www.shoesensation.com/"
    api_url = "https://www.shoesensation.com/storelocator/index/loadstore/?curPage={}"

    session = SgRequests()

    for i in range(1, 1000):
        urls = []
        hours = []
        r = session.get(api_url.format(i))
        js = r.json()["storesjson"]

        for j in js:
            urls.append(f'{url}{j.get("rewrite_request_path")}')

        with futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {executor.submit(get_hours, url): url for url in urls}
            for future in futures.as_completed(future_to_url):
                hours.append(future.result())

        hours = {k: v for element in hours for k, v in element.items()}

        for j in js:
            locator_domain = url
            location_name = j.get("store_name")
            street_address = clean_adr(j.get("address")) or "<MISSING>"
            city = j.get("city") or "<MISSING>"
            state = j.get("state") or "<MISSING>"
            postal = j.get("zipcode") or "<MISSING>"
            country_code = j.get("country_id") or "<MISSING>"
            page_url = f'{url}{j.get("rewrite_request_path")}'
            store_number = get_id(page_url)
            phone = j.get("phone") or "<MISSING>"
            latitude = j.get("latitude") or "<MISSING>"
            longitude = j.get("longitude") or "<MISSING>"
            location_type = "<MISSING>"
            hours_of_operation = hours.get(store_number)

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

            _id = (store_number, page_url)
            if _id not in s:
                s.add(_id)
                out.append(row)

        if len(js) < 35:
            break
    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
