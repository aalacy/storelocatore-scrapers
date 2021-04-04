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
    session = SgRequests()

    locator_domain = "https://www.ynhh.org/"

    for i in range(1, 5000):
        api_url = f"https://www.ynhh.org/find-a-location/locations-and-facilities.aspx?page={i}"
        r = session.get(api_url)
        tree = html.fromstring(r.text)
        divs = tree.xpath("//div[@class='module search-details']")

        for d in divs:
            line = d.xpath(".//address/text()")
            line = list(filter(None, [l.strip() for l in line]))

            index = 0
            for l in line:
                if l[0].isdigit():
                    break
                index += 1

            street_address = " ".join(", ".join(line[index:-1]).split())
            line = line[-1]
            city = line.split(",")[0].strip()
            line = line.split(",")[1].strip()
            state = line.split()[0].strip()
            try:
                postal = line.split()[1].strip()
            except IndexError:
                postal = "<MISSING>"
            country_code = "US"
            store_number = "<MISSING>"
            page_url = "https://www.ynhh.org" + "".join(d.xpath(".//h3/a/@href"))
            location_name = "".join(d.xpath(".//h3/a/text()")).strip()
            try:
                phone = d.xpath(".//span[@class='number']/text()")[0].strip()
                if phone.find("(") != -1:
                    phone = phone.split("(")[0].strip()
                if not phone[0].isdigit():
                    phone = "<MISSING>"
            except IndexError:
                phone = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            location_type = "<MISSING>"

            _tmp = []
            tr = d.xpath(".//div[@class='col-sm-4']//tr")
            for t in tr:
                try:
                    day = t.xpath("./td/strong/text()")[0].strip()
                    time = t.xpath("./td/text()")[0].strip()
                    _tmp.append(f"{day}: {time}")
                except:
                    break

            if len(tr) > 7:
                _tmp = []
            hours_of_operation = ";".join(_tmp) or "<MISSING>"

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

        if len(divs) < 10:
            break

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
