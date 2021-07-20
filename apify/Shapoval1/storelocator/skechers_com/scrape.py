import csv
from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
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

    locator_domain = "https://www.skechers.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    session = SgRequests()
    data = '{"request":{"appkey":"8C3F989C-6D95-11E1-9DE0-BB3690553863","formdata":{"objectname":"Account::Country"}}}'

    r = session.post(
        "https://hosted.where2getit.com/skechers/rest/getlist?lang=en_US&like=0.1854421036538354",
        headers=headers,
        data=data,
    )
    js = r.json()["response"]["collection"]
    states = []
    for j in js:
        state = j.get("name")
        states.append(state)

    for s in states:

        url = f"https://hosted.where2getit.com/skechers/ajax?&xml_request=%3Crequest%3E%3Cappkey%3E8C3F989C-6D95-11E1-9DE0-BB3690553863%3C%2Fappkey%3E%3Cformdata+id%3D%22getlist%22%3E%3Cobjectname%3EStoreLocator%3C%2Fobjectname%3E%3Corder%3Erank%3C%2Forder%3E%3Climit%3E1000%3C%2Flimit%3E%3Cwhere%3E%3Ccountry%3E%3Ceq%3E{s}%3C%2Feq%3E%3C%2Fcountry%3E%3C%2Fwhere%3E%3C%2Fformdata%3E%3C%2Frequest%3E"

        session = SgRequests()

        r = session.get(url, headers=headers)
        tree = html.fromstring(r.content)
        div = tree.xpath("//poi")
        for d in div:
            ad = "".join(d.xpath(".//address1/text()")) or "<MISSING>"

            street_address = "<MISSING>"
            if ad != "<MISSING>":
                a = parse_address(International_Parser(), ad)
                street_address = (
                    f"{a.street_address_1} {a.street_address_2}".replace(
                        "None", ""
                    ).strip()
                    or "<MISSING>"
                )
            city = "".join(d.xpath(".//city/text()")) or "<MISSING>"
            postal = "".join(d.xpath(".//postalcode/text()")) or "<MISSING>"
            state = (
                "".join(d.xpath(".//state/text()"))
                or "".join(d.xpath(".//province/text()"))
                or "<MISSING>"
            )
            phone = "".join(d.xpath(".//phone/text()")) or "<MISSING>"
            if phone == "-":
                phone = "<MISSING>"
            country_code = "".join(d.xpath(".//country/text()")) or "<MISSING>"
            if country_code == "CA":
                state = "".join(d.xpath(".//province/text()")) or "<MISSING>"
            store_number = "".join(d.xpath(".//storeid/text()")) or "<MISSING>"
            if not store_number.isdigit():
                store_number = "<MISSING>"
            location_name = "".join(d.xpath(".//name/text()")) or "<MISSING>"
            latitude = "".join(d.xpath(".//latitude/text()")) or "<MISSING>"
            longitude = "".join(d.xpath(".//longitude/text()")) or "<MISSING>"
            location_type = "<MISSING>"
            page_url = "https://www.skechers.com/store-locator.html"
            days = ["mon", "tues", "wed", "thurs", "fri", "sat", "sun"]
            tmp = []
            for da in days:
                day = da
                time = "".join(d.xpath(f".//r{da}/text()")) or "<MISSING>"
                line = f"{day} {time}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp)
            if hours_of_operation.count("<MISSING>") == 7:
                hours_of_operation = "<MISSING>"
            if (
                hours_of_operation.count("CLOSED") == 7
                or hours_of_operation.count("Closed") == 7
            ):
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
