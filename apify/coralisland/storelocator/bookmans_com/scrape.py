import csv
from lxml import etree
from sgselenium import SgChrome
from sglogging import SgLogSetup
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


base_url = "https://bookmans.com"
logger = SgLogSetup().get_logger("bookmans_com")


def validate(item):
    if type(item) == list:
        item = " ".join(item)
    while True:
        if item[-1:] == " ":
            item = item[:-1]
        else:
            break
    return item.replace("\u2014", "-").strip()


def get_value(item):
    if item is None:
        item = "<MISSING>"
    item = validate(item)
    if item == "":
        item = "<MISSING>"
    return item


def eliminate_space(items):
    rets = []
    for item in items:
        item = validate(item)
        if item != "":
            rets.append(item)
    return rets


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        for row in data:
            writer.writerow(row)


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
    driver = SgChrome(user_agent=user_agent).driver()

    output_list = []
    url = "https://bookmans.com/"

    sleep_time = 30
    for i in range(5):
        driver.get(url)
        driver.implicitly_wait(sleep_time)

        response = etree.HTML(driver.page_source)
        store_list = response.xpath('//div[contains(@class, "sh-accordion-item")]')
        if store_list:
            break
        else:
            sleep_time += 10
            continue

    hours = ""
    hours += get_value(
        response.xpath('//div[@class="footer-inner"]//h2//text()')
    ).split("\n\t\t")[0]
    hours += get_value(
        eliminate_space(response.xpath('//div[@class="footer-hours"]//text()'))
    )
    hours = hours.split("open from")[1].split("Holiday")[0].strip()

    for store in store_list:
        title = get_value(store.xpath(".//span[@class='sh-accordion-title']//text()"))
        address_info = eliminate_space(
            store.xpath(".//div[@class='fw-page-builder-content']//text()")
        )

        output = []
        output.append(base_url)  # url
        output.append(title)  # location name
        output.append(address_info[1])  # address
        output.append(address_info[2].split(", ")[0])  # city
        output.append(address_info[2].split(", ")[1].split(" ")[0])  # state
        output.append(address_info[2].split(", ")[1].split(" ")[1])  # zipcode
        output.append("US")  # country code
        output.append("<MISSING>")  # store_number
        phone = address_info[3]
        if "-" not in phone:
            phone = address_info[4]
        output.append(phone)  # phone
        output.append("<MISSING>")  # location type
        output.append("<MISSING>")  # latitude
        output.append("<MISSING>")  # longitude
        output.append(hours)  # opening hours
        output.append(url)
        output_list.append(output)
    driver.close()
    return output_list


def scrape():
    logger.info("Scraping Started...")
    data = fetch_data()
    write_output(data)
    logger.info(f"Scraping Finished | Total Store Count: {len(data)}")


if __name__ == "__main__":
    scrape()
