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


def gen_urls():
    urls = []
    session = SgRequests()
    r = session.get("http://www.wirelesstoyz.com/locator.php")
    tree = html.fromstring(r.text)
    states = tree.xpath("//select[@name='states']/option/@value")

    text = "".join(tree.xpath("//script[contains(text(),'cities[0]')]/text()")).strip()
    text = (
        text.split('cities[0]=""')[1]
        .split("function updatecities")[0]
        .replace(";", "")
        .strip()
        .split("\n")
    )
    for s, t in zip(states, text):
        cities = eval(t.split("=")[1])
        for city in cities[1:]:
            c = city.split("|")[0]
            urls.append(
                f"http://www.wirelesstoyz.com/locator.php?states={s}&cities={c}&locateStore=View+Stores"
            )

    return urls


def fetch_data():
    out = []
    s = set()
    session = SgRequests()
    locator_domain = "http://www.wirelesstoyz.com/"
    urls = gen_urls()

    for page_url in urls:
        r = session.get(page_url)
        tree = html.fromstring(r.text)
        divs = tree.xpath(
            "//div[@style='border-bottom:1px dotted #DDD; padding-bottom:8px']"
        )

        for d in divs:
            location_name = (
                "".join(d.xpath(".//a[@class='mapicon']/text()"))
                .replace("-", "")
                .strip()
            )
            line = d.xpath("./text()")
            line = list(filter(None, [l.strip() for l in line]))
            street_address = line[0]
            line = line[-1]
            city = location_name
            state = line.split(",")[0]
            postal = line.split(",")[1].strip()
            country_code = "US"
            store_number = "<MISSING>"
            phone = (
                "".join(d.xpath("./div[@class='listingPhone']/text()")).strip()
                or "<MISSING>"
            )
            latitude = "<MISSING>"
            longitude = "<MISSING>"
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

            check = tuple(row[2:6])
            if check not in s:
                s.add(check)
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
