import csv
import usaddress
from lxml import html
from sgrequests import SgRequests
from concurrent import futures


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
    r = session.get("https://www.moesoriginalbbq.com/#location-list-section")
    tree = html.fromstring(r.content)
    return set(tree.xpath("//h2/a/@href"))


def get_data(url):
    locator_domain = "https://www.moesoriginalbbq.com"
    page_url = "".join(url)
    if page_url.find("st-george") != -1:
        page_url = "https://www.moesoriginalbbq.com/st-george"
    if page_url.find("http://www.moesbbqtahoe.com/") != -1:
        return
    if page_url.find("https://moesbbqcharlotte.com/") != -1:
        return
    if page_url.find("https://www.moesdenver.com") != -1:
        return
    if page_url.find("https://www.moesoriginalbbq.com/mexico-city") != -1:
        return
    session = SgRequests()
    tag = {
        "Recipient": "recipient",
        "AddressNumber": "address1",
        "AddressNumberPrefix": "address1",
        "AddressNumberSuffix": "address1",
        "StreetName": "address1",
        "StreetNamePreDirectional": "address1",
        "StreetNamePreModifier": "address1",
        "StreetNamePreType": "address1",
        "StreetNamePostDirectional": "address1",
        "StreetNamePostModifier": "address1",
        "StreetNamePostType": "address1",
        "CornerOf": "address1",
        "IntersectionSeparator": "address1",
        "LandmarkName": "address1",
        "USPSBoxGroupID": "address1",
        "USPSBoxGroupType": "address1",
        "USPSBoxID": "address1",
        "USPSBoxType": "address1",
        "BuildingName": "address2",
        "OccupancyType": "address2",
        "OccupancyIdentifier": "address2",
        "SubaddressIdentifier": "address2",
        "SubaddressType": "address2",
        "PlaceName": "city",
        "StateName": "state",
        "ZipCode": "postal",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    ad = (
        " ".join(
            tree.xpath(
                '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//p[contains(text(), "Address")]/a/text() | //div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//h3/a/strong/text() | //div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//p[contains(text(), "Address")]/a/text()'
            )
        )
        .replace("\n", "")
        .strip()
    )
    if page_url.find("http://www.moesoriginalbbq.com/lo/newark/") != -1:
        ad = " ".join(
            tree.xpath(
                '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//h3/strong/text()'
            )
        )
    if page_url.find("http://www.moesoriginalbbq.com/lo/steamboat") != -1:
        ad = " ".join(
            tree.xpath(
                '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//h2/a/text()'
            )
        )
    if page_url.find("http://www.moesoriginalbbq.com/lo/tuscaloosa/") != -1:
        ad = " ".join(
            tree.xpath(
                '//div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//h2/a/text()'
            )
        )
    if page_url.find("http://www.moesoriginalbbq.com/lo/westmobile") != -1:
        ad = " ".join(
            tree.xpath(
                '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//p[./strong[contains(text(), "Address")]]/a/strong/text()'
            )
        )
    if page_url.find("https://www.moesoriginalbbq.com/durham") != -1:
        ad = " ".join(
            tree.xpath(
                '//div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//p[./strong[contains(text(), "Address")]]/a/strong/text()'
            )
        )
    if page_url.find("http://www.moesoriginalbbq.com/lo/orange-beach/") != -1:
        ad = " ".join(
            tree.xpath(
                '//div[./div[@class="col sqs-col-2 span-2"]]/following-sibling::div[1]//p[./strong[contains(text(), "Address")]]/a/strong/text()'
            )
        )
    if page_url.find("http://www.moesoriginalbbq.com/lo/eagle/") != -1:
        ad = " ".join(
            tree.xpath(
                '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//p/a/strong[contains(text(), "Address")]/text()'
            )
        )
    if page_url.find("http://www.moesoriginalbbq.com/lo/atlanta/") != -1:
        ad = " ".join(
            tree.xpath(
                '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//h2/a/strong/em/text()'
            )
        )
    if page_url.find("http://www.moesoriginalbbq.com/destin") != -1:
        ad = " ".join(
            tree.xpath(
                '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//p[./strong[contains(text(), "Address")]]/a/strong/text()'
            )
        )
    if page_url.find("http://www.moesoriginalbbq.com/lo/montgomery") != -1:
        ad = " ".join(
            tree.xpath(
                '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//h2/a/strong/text()'
            )
        )
    if page_url.find("http://www.moesoriginalbbq.com/lo/woodfin/") != -1:
        ad = " ".join(
            tree.xpath(
                '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//p[./strong[contains(text(), "Address")]]/a/strong/text()'
            )
        )
    if page_url.find("http://www.moesoriginalbbq.com/lo/mobile/") != -1:
        ad = " ".join(
            tree.xpath(
                '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//p[./strong[contains(text(), "Address")]]/a/strong/text()'
            )
        )
    if page_url.find("http://www.moesoriginalbbq.com/huntsville") != -1:
        ad = " ".join(
            tree.xpath(
                '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//p[./strong[contains(text(), "Address")]]/a/strong/text()'
            )
        )
    if page_url.find("http://www.moesoriginalbbq.com/lo/nola/") != -1:
        ad = (
            " ".join(
                tree.xpath(
                    '//div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//p[contains(text(), "Address")]//text()'
                )
            )
            .replace("Address:", "")
            .strip()
        )

    if ad.find("(") != -1:
        ad = ad.split("(")[0].strip()
    if ad.find("843-") != -1:
        ad = ad.split("843-")[0].strip()
    a = usaddress.tag(ad, tag_mapping=tag)[0]

    street_address = f"{a.get('address1')} {a.get('address2')}".replace(
        "None", ""
    ).strip()
    city = a.get("city")
    state = a.get("state")
    postal = a.get("postal")
    country_code = "US"
    store_number = "<MISSING>"

    location_name = " ".join(
        tree.xpath(
            '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//h1/text() | //div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//h1/text()'
        )
    )

    if page_url.find("http://www.moesoriginalbbq.com/lo/newark/") != -1:
        location_name = " ".join(
            tree.xpath(
                '//div[./div/h1[contains(text(), "CONTACT")]]/following-sibling::div/div[1]/div[1]/div/h2//text()'
            )
        )
    phone = "".join(
        tree.xpath(
            '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//p[contains(text(), "Phone:")]/text() | //div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//h3/strong[contains(text(), "(")]/text() | //div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//strong[contains(text(), "Phone:")]/text() | //div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//strong[contains(text(), "Phone:")]/text() | //div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//h3/following-sibling::p/text() | //div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//p[contains(text(), "Phone")]//text()'
        )
    )
    if page_url.find("http://www.moesoriginalbbq.com/bentcreek") != -1:
        phone = "".join(tree.xpath('//a[contains(@href, "tel")]/text()'))
    if page_url.find("http://www.moesoriginalbbq.com/lo/pawleysisland") != -1:
        phone = "".join(
            tree.xpath(
                '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//a[contains(@href, "tel")]/strong/text()'
            )
        )
    phone = (
        phone.replace("PORK ", "")
        .replace("RIBS(", "(")
        .replace("RIBS ", "")
        .replace("(4BBQ)", "")
    )
    if phone.find("Phone:") != -1:
        phone = phone.split("Phone:")[1].strip()
    if phone.find("-RIBS") != -1:
        phone = "<MISSING>"

    ll = (
        "".join(
            tree.xpath(
                '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//a[contains(@href, "google.com/maps")]/@href | //div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//a[contains(@href, "google.com/maps")]/@href'
            )
        )
        or "<MISSING>"
    )
    try:
        if ll.find("ll=") != -1:
            latitude = ll.split("ll=")[1].split(",")[0]
            longitude = ll.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = ll.split("@")[1].split(",")[0]
            longitude = ll.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"
    if page_url.find("http://www.moesoriginalbbq.com/lo/guntersville") != -1:
        latitude = (
            "".join(
                tree.xpath(
                    '//div[@class="sqs-block map-block sqs-block-map"]/@data-block-json'
                )
            )
            .split('"markerLat":')[1]
            .split(",")[0]
        )
        longitude = (
            "".join(
                tree.xpath(
                    '//div[@class="sqs-block map-block sqs-block-map"]/@data-block-json'
                )
            )
            .split('"markerLng":')[1]
            .split(",")[0]
        )

    location_type = "<MISSING>"

    hours_of_operation = (
        " ".join(
            tree.xpath(
                '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//h2[contains(text(), "11am")]/text() | //div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//strong[contains(text(), "11am")]/text() | //div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//em[contains(text(), "11am")]/text() | //div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//strong[contains(text(), "HOURS")]/text() | //div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//strong[contains(text(), "11am")]/text() | //div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//strong[contains(text(), "Dining Room")]/text() | //div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//h2[contains(text(), "Hours")]/text() | //div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//h2[contains(text(), "11am")]/text() | //div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//strong[contains(text(), "Dining Room and")]/text() | //div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//h2[contains(text(), "Monday")]/text()'
            )
        )
        .replace("\n", "")
        .strip()
    )

    if page_url.find("https://www.moesoriginalbbq.com/priceville") != -1:
        hours_of_operation = " ".join(
            tree.xpath(
                '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//h2[contains(text(), "Hours")]/text()'
            )
        )
    if (
        page_url.find(
            "http://www.moesoriginalbbq.com/lo/huntsvillevillageofprovidence/"
        )
        != -1
    ):
        hours_of_operation = " ".join(
            tree.xpath(
                '//div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//h2[contains(text(), "Kitchen")]/text()'
            )
        )
    if page_url.find("http://www.moesoriginalbbq.com/huntsville") != -1:
        hours_of_operation = " ".join(
            tree.xpath(
                '//div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//h2[contains(text(), "Kitchen")]/text()'
            )
        )
    if page_url.find("http://www.moesoriginalbbq.com/lo/orange-beach/") != -1:
        hours_of_operation = " ".join(
            tree.xpath(
                '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//strong[contains(text(), "NOW OPEN")]/text()'
            )
        )
    if page_url.find("https://www.moesoriginalbbq.com/st-george") != -1:
        hours_of_operation = " ".join(
            tree.xpath(
                '//div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//em[contains(text(), "11am")]/text()'
            )
        )
    if page_url.find("http://www.moesoriginalbbq.com/lo/asheville/") != -1:
        hours_of_operation = " ".join(
            tree.xpath(
                '//div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//h2[contains(text(), "11am")]/text()'
            )
        )
    if page_url.find("https://www.moesoriginalbbq.com/lo/boulder") != -1:
        hours_of_operation = " ".join(
            tree.xpath(
                '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//h2[contains(text(), "Open to in-house and patio dining.")]/text()'
            )
        )
    if page_url.find("http://www.moesoriginalbbq.com/lo/mobile/") != -1:
        hours_of_operation = " ".join(
            tree.xpath(
                '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//strong[contains(text(), "Hours")]/text()'
            )
        )
    if page_url.find("http://www.moesoriginalbbq.com/hillcrest/") != -1:
        hours_of_operation = " ".join(
            tree.xpath(
                '//div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//h2[contains(text(), "11am")]/text()'
            )
        )
    if page_url.find("http://www.moesoriginalbbq.com/lo/tuscaloosa") != -1:
        hours_of_operation = " ".join(
            tree.xpath(
                '//div[./div[@class="col sqs-col-4 span-4"]]/following-sibling::div[1]//h2[contains(text(), "Daily")]/text()'
            )
        )
    if page_url.find("http://www.moesoriginalbbq.com/lo/guntersville") != -1:
        hours_of_operation = " ".join(
            tree.xpath(
                '//div[./div[@class="col sqs-col-3 span-3"]]/following-sibling::div[1]//h2[./strong]//text()'
            )
        )

    hours_of_operation = (
        hours_of_operation.replace("Open to in-house and patio dining.", "")
        .replace("NOW OPEN:", "")
        .strip()
    )

    if hours_of_operation.find("Kitchen:") != -1:
        hours_of_operation = (
            hours_of_operation.split("Kitchen:")[1].split("Bar:")[0].strip()
        )
    if hours_of_operation.find("Curbside") != -1:
        hours_of_operation = hours_of_operation.split("Curbside")[0].strip()
    if (
        hours_of_operation.find(
            "Dining Room & Patio, Take Out and Delivery plus Catering Available"
        )
        != -1
    ):
        hours_of_operation = (
            hours_of_operation.split("HOURS: ")[1].split("Dining")[0].strip()
        )
    if (
        hours_of_operation.find(
            "Dining Room and Drive Thru Open plus Take Out & Delivery"
        )
        != -1
    ):
        hours_of_operation = hours_of_operation.split(
            "Dining Room and Drive Thru Open plus Take Out & Delivery"
        )[1].strip()
    if hours_of_operation.find("Kitchen") != -1:
        hours_of_operation = (
            hours_of_operation.split("Kitchen")[1].split("Bar:")[0].strip()
        )
    if (
        hours_of_operation.find(
            "Dining Room & Patio Open, Take Out and Delivery plus Catering Available"
        )
        != -1
    ):
        hours_of_operation = hours_of_operation.replace(
            "Dining Room & Patio Open, Take Out and Delivery plus Catering Available",
            "",
        ).strip()
    if hours_of_operation.find("Hours:  Restaurant ") != -1:
        hours_of_operation = (
            hours_of_operation.split("Hours:  Restaurant ")[1].split("Bar")[0].strip()
        )

    hours_of_operation = (
        hours_of_operation.replace("DINE IN NOW AVAILABLE!", "")
        .replace("Dining Room and Patio Open plus Take Out & Catering", "")
        .replace("Address:", "")
        .strip()
    )
    hours_of_operation = (
        hours_of_operation.replace("Hours (dine in and drive thru)", "")
        .replace("Dine in and Carry Out Available", "")
        .replace("Open:", "")
        .strip()
    )
    hours_of_operation = (
        hours_of_operation.replace(
            "Take out and third party delivery thru Door Dash also available.", ""
        )
        .replace("NOW OPEN", "")
        .replace("Hours of operation:", "")
        .strip()
    )

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
