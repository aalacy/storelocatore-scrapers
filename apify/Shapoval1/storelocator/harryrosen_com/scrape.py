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

    locator_domain = "https://www.harryrosen.com"
    api_url = "https://www.harryrosen.com/en/stores"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = "".join(tree.xpath('//script[contains(text(), "ctas")]/text()'))
    js = json.loads(jsblock)

    for j in js["props"]["pageProps"]["genericPageContent"]["items"][1]["tabs"]:
        a = j.get("content").get("items")
        for b in a:
            l = b.get("ctas")
            if l is None:
                continue

            slug = l[0].get("link")
            ad = b.get("body")
            ad = html.fromstring(ad)
            ad = ad.xpath("//*//text()")
            adr = "".join(ad[1]).replace("\n", "").strip() or "<MISSING>"
            page_url = f"{locator_domain}{slug}"
            location_name = b.get("headline")
            location_type = "<MISSING>"
            street_address = "".join(ad[0]).strip()

            if street_address.find("ADDRESS") != -1:
                street_address = "".join(ad[1]).strip()
                adr = "".join(ad[2]).replace("\n", "").strip()
            if street_address.find("100 King Street West Toronto") != -1:
                adr = " ".join(ad[0].split()[3:])
                street_address = " ".join(street_address.split()[:3])
            adr = adr.replace(",", "")

            state = adr.split()[-3]
            postal = " ".join(adr.split()[-2:])

            country_code = "CA"
            city = " ".join(adr.split()[:-3])
            store_number = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"

            phone = "".join(ad[2]).replace("\n", "").strip() or "<MISSING>"
            if phone == "<MISSING>":
                phone = "".join(ad[3]).replace("\n", "").strip() or "<MISSING>"
            if street_address.find("1455") != -1:
                phone = "".join(ad[4]).replace("\n", "").strip()
            phone = phone.replace("Tel:", "").strip()
            if phone.find("This") != -1:
                phone = phone.split("This")[0].strip()

            hours_of_operation = " ".join(ad).replace("\n", "").strip()
            if hours_of_operation.find("STORE HOURS") != -1:
                hours_of_operation = hours_of_operation.split("STORE HOURS")[1].strip()
            if hours_of_operation.find("temporarily closed") != -1:
                hours_of_operation = "temporarily closed"
            if (
                hours_of_operation.find("closed") != -1
                and hours_of_operation.find("temporarily closed") == -1
            ):
                hours_of_operation = "closed"

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
