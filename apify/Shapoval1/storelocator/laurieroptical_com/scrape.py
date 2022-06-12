import csv
import time
from lxml import html
from sgselenium import SgFirefox
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

    locator_domain = "https://www.laurier-optical.com/"
    page_url = "https://www.laurier-optical.com/eye-exam-ottawa"
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    div = tree.xpath('//h2[@style="font-size:38px"]')
    i = 0
    b = 0
    for d in div:
        location_name = "".join(d.xpath(".//text()"))
        page_url = "https://www.laurier-optical.com/eye-exam-ottawa"
        mon = (
            " ".join(d.xpath('.//following::*[contains(text(), "Monday")][1]/text()'))
            .replace("\n", "")
            .strip()
        )
        tue = (
            " ".join(d.xpath('.//following::*[contains(text(), "Tuesday")][1]/text()'))
            .replace("\n", "")
            .strip()
        )
        wed = (
            " ".join(
                d.xpath('.//following::*[contains(text(), "Wednesday")][1]/text()')
            )
            .replace("\n", "")
            .strip()
        )
        thu = (
            " ".join(d.xpath('.//following::*[contains(text(), "Thursday")][1]/text()'))
            .replace("\n", "")
            .strip()
        )
        fri = (
            " ".join(d.xpath('.//following::*[contains(text(), "Friday")][1]/text()'))
            .replace("\n", "")
            .strip()
        )
        sat = (
            " ".join(d.xpath('.//following::*[contains(text(), "Saturday")][1]/text()'))
            .replace("\n", "")
            .strip()
        )
        sun = (
            " ".join(d.xpath('.//following::*[contains(text(), "Sunday")][1]/text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            mon + " " + tue + " " + wed + " " + thu + " " + fri + " " + sat + " " + sun
        )
        phone = "".join(
            d.xpath('.//following::*[contains(text(), "+1")][1]/text()')
        ).strip()
        adr = []
        maps = []
        with SgFirefox() as fox:
            fox.get(page_url)
            time.sleep(10)
            iframes = fox.find_elements_by_xpath("//iframe")
            for iframe in iframes:
                fox.switch_to.frame(iframe)
                root = html.fromstring(fox.page_source)
                urls = root.xpath(".//a/@href")
                adr.append(urls[0])
                maps.append(urls[1])
                fox.switch_to.default_content()
        ad = adr[i]
        ad = (
            "".join(ad)
            .split("destination=")[1]
            .split("Canada")[0]
            .replace("%20", " ")
            .replace("Orl%C3%A9ans", "Orleans")
        )
        i += 1
        street_address = ad.split(",")[0].strip()
        city = ad.split(",")[1].strip()
        state = ad.split(",")[2].split()[0].strip()
        country_code = "CA"
        postal = " ".join(ad.split(",")[2].split()[1:]) or "<MISSING>"
        store_number = "<MISSING>"
        text = maps[b]
        b += 1
        latitude = "".join(text).split("ll=")[1].split(",")[0]
        longitude = "".join(text).split("ll=")[1].split(",")[1].split("&")[0]
        location_type = "<MISSING>"
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

    page_url = "https://www.laurier-optical.com/eye-exam-ontario"
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[./div/h4]")
    for d in div:
        location_name = "".join(d.xpath(".//h4//text()"))
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if location_name.find("Brockville") != -1:
            latitude = "44.600913"
            longitude = "-75.706722"
        if location_name.find("Kanata") != -1:
            latitude = "45.311309"
            longitude = "-75.915883"
        if location_name.find("Kingston") != -1:
            latitude = "44.256408"
            longitude = "-76.570854"
        if location_name.find("Belleville") != -1:
            latitude = "44.187003"
            longitude = "-77.395199"
        if location_name.find("Cornwall") != -1:
            latitude = "45.016397"
            longitude = "-74.726121"
        ad = "".join(d.xpath('.//p//span[@style="font-size:14px"]//text()')).replace(
            "945,", "945"
        )
        street_address = ad.split(",")[0].strip()
        city = ad.split(",")[1].strip()
        state = ad.split(",")[2].split()[0]
        postal = " ".join(ad.split(",")[2].split()[1:])
        country_code = "CA"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = "".join(d.xpath('.//p[contains(text(), "+1")]//text()'))
        hours_of_operation = (
            " ".join(
                d.xpath('.//p[contains(text(), "+1")]/following-sibling::p/text()')
            )
            .replace("\n", "")
            .strip()
        )
        page_url = "".join(d.xpath('.//a[./span[contains(text(), "Show More")]]/@href'))
        if page_url.find("https://www.laurier-optical.com/eye-exam-ottawa") != -1:
            continue

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

    api_url = "https://www.laurier-optical.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        "//a[.//p[text()='Locations']]/following-sibling::ul/li[7]/following-sibling::li/a"
    )

    for d in div:
        page_url = "".join(d.xpath(".//@href"))
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//h1//text()"))
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        ad = "".join(
            tree.xpath(
                '//div[./h2//span[text()="Our Location"]]/following-sibling::div[1]//text()'
            )
        )
        if location_name.find("Aylmer") != -1:
            ad = ad.split("center in ")[1].split("where")[0].strip()
            latitude = "45.395003"
            longitude = "-75.831351"
        if location_name.find("Hull") != -1:
            ad = ad.split("de Hull,")[1].split(".")[0].strip()
            latitude = "45.441389"
            longitude = "-75.731841"
        if location_name.find("Gatineau") != -1:
            ad = ad.split("Gatineau in")[1].split("and")[0].strip()
            latitude = "45.475657"
            longitude = "-75.699474"
        location_type = "<MISSING>"
        street_address = ad.split(",")[0].strip()
        phone = "".join(tree.xpath('//p[contains(text(), "+1")]/text()'))
        state = ad.split(",")[2].split()[0].strip()
        postal = " ".join(ad.split(",")[2].split()[1:])
        country_code = "CA"
        city = ad.split(",")[1].strip()
        store_number = "<MISSING>"
        hours_of_operation = (
            " ".join(
                tree.xpath('//p[contains(text(), "+1")]/following-sibling::p//text()')
            )
            .replace("\n", "")
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
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
