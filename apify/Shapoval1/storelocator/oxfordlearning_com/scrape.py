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
    locator_domain = "https://www.oxfordlearning.com"
    api_urls = [
        "https://gradepowerlearning.com/locations/#location-filter-postal",
        "https://www.oxfordlearning.com/locations/",
    ]
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    for api_url in api_urls:
        r = session.get(api_url, headers=headers)

        tree = html.fromstring(r.text)
        div = tree.xpath(
            '//section[not(@id="olc-cat-313")]//a[contains(text(), "Location Details")]'
        )
        s = set()
        for d in div:
            page_url = "".join(d.xpath(".//@href"))

            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)

            location_name = (
                " ".join(tree.xpath('//h1[@itemprop="name"]/text()[1]'))
                .replace("\n", "")
                .strip()
            )
            street_address = "".join(
                tree.xpath('//span[@itemprop="streetAddress"]/text()')
            ).strip()
            street_address = (
                street_address.replace("The Village at Lee Branch", "")
                .replace("Southlands Mall in SE Aurora", "")
                .replace("Maynard Crossing Shopping Centre", "")
                .strip()
            )
            street_address = (
                street_address.replace("College Park Plaza Shopping Centre", "")
                .replace("Knell’s Ridge Square", "")
                .replace("Now Open", "")
                .strip()
            )
            street_address = (
                street_address.replace("MarketPlace at Callingwood", "")
                .replace("Windermere Gate Plaza", "")
                .replace("NOW OPEN", "")
                .replace("Panorama Shopping Village", "")
                .strip()
            )
            street_address = (
                street_address.replace("Now Open!", "")
                .replace("North Ajax Market Place", "")
                .replace("Fletcher's Meadow Plaza", "")
                .replace("Conestoga Square", "")
                .strip()
            )
            street_address = (
                street_address.replace(
                    "Springdale Plaza Unit # 25, Springdale Plaza", ""
                )
                .replace("Unit #6 Unit #6", "Unit #6")
                .replace("Unit #2 Unit #2", "Unit #2")
                .strip()
            )
            street_address = (
                street_address.replace("Halton Gate Plaza", "")
                .replace("Riverview Shopping Centre", "")
                .replace("We've Moved!", "")
                .replace("Unit A5 Unit A5", "Unit A5")
                .replace("Town Centre Plaza", "")
                .strip()
            )
            street_address = (
                street_address.replace(
                    "Markham Boxgrove Plaza Unit 3, Markham Boxgrove Plaza", ""
                )
                .replace("Markham, Ontario", "")
                .replace("East Unit 2nd Floor, East Unit", "")
                .strip()
            )
            street_address = (
                street_address.replace("Unit 20 Unit 20", "Unit 20")
                .replace("East Tomken Shopping Centre Tomken Shopping Centre", "")
                .replace("Unit 5 Unit 5", "Unit 5")
                .strip()
            )
            street_address = (
                street_address.replace("Maple Grove Village", "")
                .replace("Suite 201 Suite 201", "Suite 201")
                .replace("Unit 15 Unit 15", "Unit 15")
                .replace("Donwood Plaza Unit 1, Donwood Plaza", "")
                .strip()
            )
            street_address = (
                street_address.replace("Humbertown Shopping Centre", "")
                .replace("Suite 9 Suite 9", "Suite 9")
                .replace("Suite 200 Suite 200", "Suite 200")
                .strip()
            )
            street_address = (
                street_address.replace("Unit B Unit B", "Unit B")
                .replace("Guildwood Village Shopping Centre", "")
                .replace("Abbey Lane Plaza", "")
                .replace("North Cedar's Plaza", "")
                .strip()
            )
            street_address = (
                street_address.replace("Unit A5 Unit A5", "Unit A5")
                .replace("Markham Boxgrove Plaza Unit 3, Markham Boxgrove Plaza", "")
                .replace("Blue Haven Shopping Village", "")
                .strip()
            )
            street_address = street_address.replace(",", "").strip()
            city = (
                "".join(tree.xpath('//span[@itemprop="addressLocality"]/text()'))
                .replace(",", "")
                .strip()
            )
            state = "".join(
                tree.xpath('//span[@itemprop="addressRegion"]/text()')
            ).strip()
            country_code = "CA"
            postal = "".join(
                tree.xpath('//span[@itemprop="postalCode"]/text()')
            ).strip()
            if postal.find("-") != -1:
                postal = postal.split("-")[0].strip()
            if postal.isdigit():
                country_code = "US"

            store_number = "<MISSING>"
            phone = (
                "".join(tree.xpath('//p[./a[contains(@href, "tel")]]//text()'))
                .replace("\n", "")
                .strip()
            )
            if phone.find("LIRE") != -1:
                phone = (
                    phone.replace("LIRE", "")
                    .replace(" ", "")
                    .replace("(", "")
                    .replace(")", "")
                    .strip()
                )
            if phone.find(" ") != -1:
                phone = phone.split()[0].strip()
            ll = "".join(
                tree.xpath('//script[contains(text(), "var olc_elements =")]/text()')
            )
            try:
                latitude = (
                    ll.split(f"{phone}")[1]
                    .split('"latitude":"')[1]
                    .split('"')[0]
                    .strip()
                )
                longitude = (
                    ll.split(f"{phone}")[1]
                    .split('"longitude":"')[1]
                    .split('"')[0]
                    .strip()
                )
            except:
                latitude = (
                    ll.split("450.510.LIRE (5473)")[1]
                    .split('"latitude":"')[1]
                    .split('"')[0]
                    .strip()
                )
                longitude = (
                    ll.split("450.510.LIRE (5473)")[1]
                    .split('"longitude":"')[1]
                    .split('"')[0]
                    .strip()
                )

            location_type = "GradePower Learning"

            hours_of_operation = tree.xpath("//dl//div//text()")
            hours_of_operation = list(
                filter(None, [a.strip() for a in hours_of_operation])
            )
            hours_of_operation = " ".join(hours_of_operation) or "<MISSING>"

            line = street_address
            if line in s:
                continue
            s.add(line)

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
