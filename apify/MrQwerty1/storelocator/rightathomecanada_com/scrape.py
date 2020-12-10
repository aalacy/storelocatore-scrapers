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
    r = session.get("https://www.rightathomecanada.com/locations")
    tree = html.fromstring(r.content)

    return set(
        tree.xpath(
            "//a[@style='font-size: 20px; line-height: 1.3; color: #00556e;']/@href"
        )
    )


def get_data(u):
    session = SgRequests()
    r = session.get(u)
    tree = html.fromstring(r.text)
    locator_domain = "https://www.rightathomecanada.com"
    line = tree.xpath("//div[@style='float:left']")[0].xpath(".//text()")

    _tmp = []
    add = False
    for l in line:
        li = l.replace("\xa0", "").replace("</br>", "").replace("\u2028", " ").strip()
        if li.startswith("#") or li[0].isdigit():
            _tmp.append(li)
            add = True
            continue
        elif li.find(",") != -1:
            _tmp.append(li)
            if len(li.split()) == 2:
                _tmp.append(line[line.index(l) + 1].strip())
            break
        if add:
            _tmp.append(li)

    if _tmp:
        if len(_tmp) == 2:
            street_address = _tmp[0]
        else:
            street_address = " ".join(_tmp[:2])

        line = _tmp[-1]
        if len(line) == 7:
            postal = line
            line = _tmp[-2]
        else:
            postal = line[-7:]
        city = line.split(",")[0]
        line = line.split(",")[1].strip()
        state = line.replace(postal, "")

    else:
        street_address = "<MISSING>"
        city = "<MISSING>"
        state = "<MISSING>"
        postal = "<MISSING>"

    phone = tree.xpath("//div[@class='mobiletel']/a/text()")[0]
    if phone.find("or") != -1:
        phone = phone.split(" or ")[0]
    try:
        text = "".join(tree.xpath("//text()"))
        latitude = re.findall(r'"latitude": "(\d{2,3}.\d+)"', text)[0]
        longitude = re.findall(r'"longitude": "(-?\d{2,3}.\d+)"', text)[0]
    except:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    page_url = u
    country_code = "CA"
    location_name = (
        "".join(tree.xpath("//p[@class='page-description']/text()"))
        .replace("-", "")
        .strip()
    )
    if location_name.find("what we do") != -1:
        location_name = f"Right at Home in {city}"
    store_number = "<MISSING>"
    location_type = "<MISSING>"
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
