import csv
import json
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
    locator_domain = "https://www.wingzone.com"
    page_url = "https://www.wingzone.com/locations"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.content)
    li = tree.xpath('//li[@class="location"]')
    for j in li:
        ad = j.xpath('.//span[@class="address"]/text()')
        ad = list(filter(None, [a.strip() for a in ad]))
        street_address = ", ".join(ad[:-1])
        line = ad[-1]
        city = line.split(",")[0]
        line = line.split(",")[1].strip()
        postal = line.split()[-1]
        state = line.replace(postal, "").replace(".", "").strip()
        country_code = "US"
        store_number = "".join(j.xpath("./@data-loc-id"))
        slug = "".join(j.xpath(".//a[@class='website btn v3 small']/@href"))
        page_url = f"{locator_domain}{slug}"
        location_name = "".join(j.xpath('.//div[@class="title"]/h4/text()'))
        phone = "".join(j.xpath('.//a[@class="phone"]/text()'))
        latitude = "".join(j.xpath("./@data-latitude")) or "<MISSING>"
        longitude = "".join(j.xpath("./@data-longitude")) or "<MISSING>"
        location_type = "<MISSING>"
        text = "".join(tree.xpath(f"//div[@data-loc-id={store_number}]/ul/@data-hours"))
        text = "[" + text.replace("][", "],[").replace("[", "{").replace("]", "}") + "]"
        js = json.loads(text)
        tmp = []
        for s in js:
            day = s.get("Interval")
            start = s.get("OpenTime")
            close = s.get("CloseTime")
            if s.get("Closed") == "1":
                line = f"{day} : Closed"
            else:
                line = f"{day} : {start} - {close}"
            tmp.append(line)

        hours_of_operation = ";".join(tmp) or "<MISSING>"
        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "Closed"
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
