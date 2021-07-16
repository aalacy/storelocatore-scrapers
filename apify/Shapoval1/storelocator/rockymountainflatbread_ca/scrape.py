import csv
import time
from sgselenium import SgSelenium
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

    locator_domain = "https://www.rockymountainflatbread.ca"
    api_url = "https://www.rockymountainflatbread.ca/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//h1/a")
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        if page_url.find("surrey") != -1:
            continue
        location_name = "".join(d.xpath(".//text()"))
        driver = SgSelenium().firefox()
        time.sleep(10)
        driver.get(page_url)
        time.sleep(10)
        iframe = driver.find_element_by_xpath('//iframe[contains(@src, "maps")]')
        driver.switch_to.frame(iframe)

        ad = driver.find_element_by_xpath("//div[@class='address']").text
        ad = "".join(ad)
        location_type = "<MISSING>"
        street_address = " ".join(ad.split(",")[:-2])
        state = ad.split(",")[-1].split()[0].strip()
        postal = " ".join(ad.split(",")[-1].split()[1:])
        country_code = "CA"
        city = ad.split(",")[-2].strip()
        store_number = "<MISSING>"
        latlon = driver.find_element_by_xpath(
            '//a[text()="View larger map"]'
        ).get_attribute("href")
        try:
            latitude = "".join(latlon).split("ll=")[1].split(",")[0].strip()
            longitude = (
                "".join(latlon).split("ll=")[1].split(",")[1].split("&")[0].strip()
            )
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        driver.switch_to.default_content()
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        phone = "<MISSING>"
        if page_url.find("banff") != -1:
            phone = "403 985 7632"
        if page_url.find("canmore") != -1:
            phone = "".join(tree.xpath('//a[./span[contains(text(), "CALL")]]/@href'))
        if page_url.find("main-street") != -1:
            phone = "".join(tree.xpath("//div/h2[2]//text()"))
        if page_url.find("kitsilano") != -1:
            phone = "".join(
                tree.xpath('//p[contains(text(), "@")]/preceding-sibling::p[1]/text()')
            )
        if page_url.find("calgary") != -1:
            phone = "".join(tree.xpath("//div/h2[2]//text()"))
        phone = phone.replace("Tel:", "").replace("tel:", "").strip()
        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="diamond-content"]//text()'))
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
