import csv
from lxml import etree
from time import sleep

from sgselenium import SgFirefox


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    items = []

    domain = "feederssupply.com"
    start_url = "https://www.feederssupply.com/store-locator"

    with SgFirefox(is_headless=True) as driver:
        driver.set_window_position(0, 0)
        driver.set_window_size(1024, 4068)
        driver.get(start_url)
        try:
            driver.find_element_by_xpath('//div[@aria-label="Back to site"]').click()
        except Exception:
            pass

        all_locations_urls = driver.find_elements_by_xpath(
            '//a[@data-testid="linkElement" and span[contains(text(), "Location Page")]]'
        )
        for i, url in enumerate(all_locations_urls):
            poi = all_locations_urls[i]
            poi.location_once_scrolled_into_view
            try:
                driver.execute_script("window.scrollBy(0, -400);")
                poi.click()
            except:
                driver.execute_script("window.scrollBy(0, -200);")
                poi.click()
            sleep(15)
            driver.save_screenshot("feeder.png")
            poi_html = etree.HTML(driver.page_source)
            raw_data = poi_html.xpath(
                '//div[@class="animating-screenIn-exit"]//div[@data-testid="mesh-container-content"]/div[3]//text()'
            )
            raw_data = [e.strip() for e in raw_data if e.strip() and len(e) > 1]

            store_url = start_url
            location_name = raw_data[0]
            location_name = location_name if location_name else "<MISSING>"
            street_address = raw_data[1]
            city = raw_data[2].split(", ")[0]
            state = raw_data[2].split(", ")[-1].split()[0]
            zip_code = raw_data[2].split(", ")[-1].split()[-1]
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            phone = raw_data[3]
            location_type = "<MISSING>"
            hoo = poi_html.xpath(
                '//p[span[span[span[span[contains(text(),"Store Hours")]]]]]/following-sibling::p[1]//text()'
            )
            hoo = [e.strip() for e in hoo if e.strip()]
            hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

            iframe = driver.find_element_by_xpath('//iframe[@title="Google Maps"]')
            driver.switch_to.frame(iframe)
            poi_html = etree.HTML(driver.page_source)
            driver.switch_to.default_content()
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            geo = poi_html.xpath('//a[contains(@href, "maps")]/@href')
            if geo:
                geo = geo[-1].split("/@")[-1].split(",")[:2]
                if len(geo) == 2:
                    latitude = geo[0]
                    longitude = geo[1]

            driver.find_element_by_xpath(
                '//div[@data-testid="popupCloseIconButtonRoot"]'
            ).click()

            item = [
                domain,
                store_url,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]

            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
