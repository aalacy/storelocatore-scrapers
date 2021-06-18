import csv

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


def get_hours(_id):
    session = SgRequests()
    r = session.get(
        f"https://knowledgetags.yextpages.net/embed?key=EwOOPFqqshYCRf_I0uRL3od4NjOoYC58Pot0yJLo_w5uAVTrvk-XLy9Y53ilVGut&account_id=1341034&location_id={_id}"
    )

    try:
        text = r.text.split('"hours":')[1].split("]")[0] + "]"
        hours = ";".join(eval(text))
    except:
        hours = "<MISSING>"

    return hours


def get_urls():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get("https://www.ivyrehab.com/locations/", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='fwpl-item el-i1ybmv button smallest']/a/@href")


def get_data(page_url):
    locator_domain = "https://www.ivyrehab.com/"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = tree.xpath("//h4[@class='h4 ff-ProximaNova-Regular']/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = line[0]
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = (
        "".join(tree.xpath("//script[contains(@src, 'location_id=')]/@src")).split("=")[
            -1
        ]
        or "<MISSING>"
    )
    phone = (
        "".join(tree.xpath("//h2[@class='phone-number']/text()")).strip() or "<MISSING>"
    )
    latitude = "".join(tree.xpath("//div[@data-lat]/@data-lat")) or "<MISSING>"
    longitude = "".join(tree.xpath("//div[@data-lat]/@data-lng")) or "<MISSING>"
    location_type = "<MISSING>"
    if store_number != "<MISSING>":
        hours_of_operation = get_hours(store_number)
    else:
        _tmp = []
        divs = tree.xpath("//div[@class='lh-day']")
        for d in divs:
            day = "".join(d.xpath("./div[1]//text()")).strip()
            time = "".join(d.xpath("./div[2]//text()")).strip()
            _tmp.append(f"{day}: {time}")

        hours_of_operation = " ".join(";".join(_tmp).split()) or "<MISSING>"

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
