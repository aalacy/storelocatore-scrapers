import csv
import re

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


def get_urls():
    session = SgRequests()
    r = session.get("https://www.ufcgym.com/locations/list/")
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='result-list--item']//a/@href")


def get_data(url):
    locator_domain = "https://www.ufcgym.com/"
    page_url = f"https://www.ufcgym.com{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'window.__NUXT__')]/text()"))
    if not text:
        return

    name, street, city, state, _zip, phone, owner, status = (
        "n",
        "str",
        "c",
        "s",
        "z",
        "p",
        "o",
        "st",
    )
    if status or owner:
        pass

    data = (
        "{name" + text.split("name")[1].split(",email")[0].replace("zip", "_zip") + "}"
    )
    _vars = text.split("=function")[1].split("{")[0].replace("(", "").replace(")", "")
    _values = text.split("}")[-1].replace("(", "").replace(")", "")
    for k, v in zip(
        _vars.split(","),
        re.split(r",(?=(?:[^\"']*[\"'][^\"']*[\"'])*[^\"']*$)", _values),
    ):
        data = data.replace(f"{k},", f"{v},")

    data = eval(data)
    location_name = data.get(name) or "<MISSING>"
    street_address = data.get(street) or "<MISSING>"
    city = data.get(city) or "<MISSING>"
    state = data.get(state) or "<MISSING>"
    postal = data.get(_zip) or "<MISSING>"
    if len(postal) == 5 or postal == "<MISSING>":
        country_code = "US"
    else:
        country_code = "CA"

    store_number = "<MISSING>"
    phone = data.get(phone) or "<MISSING>"
    latitude = "".join(re.findall(r"lat:(\d+.\d+)", text)) or "<MISSING>"
    longitude = "".join(re.findall(r"lng:(-?\d+.\d+)", text)) or "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    li = tree.xpath("//li[contains(@class, 'd-block')]")
    for l in li:
        day = "".join(l.xpath("./span/text()")).strip()
        time = "".join(l.xpath("./text()")).strip()
        _tmp.append(f"{day} {time}")

    hours_of_operation = (
        ";".join(_tmp).replace("*By Appointment Only*", "") or "Coming Soon"
    )

    if hours_of_operation.lower().count("closed") == 7:
        hours_of_operation = "Closed"
    elif hours_of_operation.lower().find("coming") != -1:
        hours_of_operation = "Coming Soon"

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

    return row


def fetch_data():
    out = []
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            if row:
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
