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
    locator_domain = "https://hattieb.com/"
    page_url = "https://hattieb.com/"

    session = SgRequests()
    r = session.get("https://hattieb.com/javascripts/main.js?v=060321")
    days = r.text.split("Closed for the Holiday</span>',")[1].split(";")[0].strip()
    closedMsg = (
        days.split("closedMsg = [")[1]
        .split("],")[0]
        .split(",")[1]
        .replace("'", "")
        .strip()
    )
    open11to4 = (
        days.split("open11to4 = [")[1]
        .split("],")[0]
        .split('<span class="hours">')[1]
        .replace("'", "")
        .split(",")[1]
        .strip()
    )
    open11to9 = (
        days.split("open11to9 = [")[1]
        .split("],")[0]
        .split('<span class="hours">')[1]
        .replace("'", "")
        .split(",")[1]
        .strip()
    )
    open11to10 = (
        days.split("open11to10 = [")[1]
        .split("],")[0]
        .split('<span class="hours">')[1]
        .replace("'", "")
        .split(",")[1]
        .strip()
    )
    open11to11 = (
        days.split("open11to11 = [")[1]
        .split("],")[0]
        .split('<span class="hours">')[1]
        .replace("'", "")
        .split(",")[1]
        .strip()
    )
    open11to12 = (
        days.split("open11to12 = [")[1]
        .split("],")[0]
        .split('<span class="hours">')[1]
        .replace("'", "")
        .split(",")[1]
        .strip()
    )

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[contains(@class, "fullinfo")]')

    for d in div:
        clas = "".join(d.xpath("./@class")).replace("fullinfo", "").strip()

        ad = " ".join(d.xpath('.//a[contains(@href, "maps")]/text()[last()]'))
        street_address = " ".join(
            d.xpath('.//a[contains(@href, "maps")]/text()[1]')
        ).strip()
        city = ad.split(",")[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        state = ad.split(",")[1].split()[0].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_name = "".join(d.xpath(f'.//preceding::a[@class="{clas}"][1]/text()'))
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()')).strip()
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"
        session = SgRequests()
        r = session.get("https://hattieb.com/javascripts/main.js?v=060321")

        hours = (
            r.text.split(f"{ad}")[1]
            .split("<br></div>'")[0]
            .split("//Saturday")[1]
            .replace("\n", "")
            .strip()
        )
        hours = (
            hours.replace("'", "")
            .replace('<div class="half-1">', "")
            .replace('<span class="red">', "")
            .replace("</span>", "")
            .replace("<br>", "")
            .strip()
        )
        hours = (
            hours.replace("[1]", "")
            .replace('<div class="half-2">', "")
            .replace("</div>", "")
            .replace("+", " ")
            .strip()
        )
        hours = (
            hours.replace("open11to10", f"{open11to10}")
            .replace("open11to12", f"{open11to12}")
            .replace("open11to4", f"{open11to4}")
            .replace("open11to9", f"{open11to9}")
        )
        hours = (
            hours.replace("open11to11", f"{open11to11}")
            .replace("closedMsg", f"{closedMsg}")
            .replace("  ", " ")
            .strip()
        )

        hours_of_operation = hours

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
