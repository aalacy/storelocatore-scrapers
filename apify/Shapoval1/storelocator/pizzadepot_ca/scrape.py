import csv
from lxml import html
from sgrequests import SgRequests
from sgselenium.sgselenium import SgFirefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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

    locator_domain = "https://www.pizzadepot.ca"
    api_url = "https://www.pizzadepot.ca/location/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)

    slug = tree.xpath('//a[.//span[contains(text(), "VIEW")]]')
    for d in slug:
        sg = "".join(d.xpath(".//@href"))
        phone = "".join(
            d.xpath(
                './/preceding::span[./i[@class="fas fa-phone-alt"]][1]/following-sibling::span[1]/text()'
            )
        ).strip()
        location_type = "<MISSING>"
        tc = "".join(d.xpath(".//preceding::h2[1]/text()"))
        if tc.find("Opening Soon") != -1:
            location_type = "Coming Soon"
        cms = "".join(d.xpath(".//preceding::div[5]//text()")).replace("\n", "").strip()
        if cms.find("Temporarily Closed") != -1:
            location_type = "Temporarily Closed"
        page_url = f"https://www.pizzadepot.ca{sg}"
        with SgFirefox() as driver:
            driver.implicitly_wait(10)
            driver.get(page_url)

            driver.maximize_window()
            driver.implicitly_wait(20)
            driver.switch_to.frame(0)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="address"]'))
            )
            ad = driver.find_element_by_xpath('//div[@class="address"]').text
            ll = driver.find_element_by_xpath(
                '//div[@class="google-maps-link"]/a'
            ).get_attribute("href")
            ll = "".join(ll)
            ad = "".join(ad)
            driver.switch_to.default_content()

            street_address = ad.split(",")[0].strip()
            state = ad.split(",")[2].split()[0].strip()
            postal = " ".join(ad.split(",")[2].split()[1:]).strip()
            country_code = "Canada"
            city = ad.split(",")[1].strip()
            location_name = city + " " + "Pizza Depot"
            store_number = "<MISSING>"
            try:
                latitude = ll.split("ll=")[1].split(",")[0].strip()
                longitude = ll.split("ll=")[1].split(",")[1].split("&")[0].strip()
            except:
                latitude, longitude = "<MISSING>", "<MISSING>"

            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            hours_of_operation = tree.xpath(
                '//div[./div/h3[contains(text(), "Hours")]]/following-sibling::div//p/text() | //div[./div/h2[contains(text(), "Hours")]]/following-sibling::div//p/text()'
            )
            hours_of_operation = list(
                filter(None, [a.strip() for a in hours_of_operation])
            )
            hours_of_operation = (
                " ".join(hours_of_operation)
                .replace("Thursday-Thursday", "Thursday")
                .replace("Sunday-Sunday", "Sunday")
                .replace("1:900", "19:00")
                or "<MISSING>"
            )
            if page_url.find("vaughan") != -1:
                hours_of_operation = "Monday-Thursday" + hours_of_operation
            if page_url.find("https://www.pizzadepot.ca/995-paisley-rd-guelph/") != -1:
                street_address = "995 Paisley Rd"
                city = "Guelph"
                state = "ON"
                postal = "N1T 2A6"
                latitude, longitude = "<MISSING>", "<MISSING>"
            tmcl = "".join(
                tree.xpath('//h3[contains(text(), "Temporarily closed")]/text()')
            )
            if tmcl:
                location_type = "Temporarily Closed"

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
