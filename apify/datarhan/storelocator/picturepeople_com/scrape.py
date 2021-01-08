import csv
from lxml import etree
from requests_toolbelt import MultipartEncoder

from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


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
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "picturepeople.com"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }

    response = session.get(
        "https://tpp.mystratus.com/20.21/(S(yvwjo2fmynyixy4hnhou1vwc))/OnlineBooking/Verify.aspx?ReferenceGUID=E3915F3B997D45ABA1E66D7F0385023F",
        headers=headers,
    )
    dom = etree.HTML(response.text)
    viewstate = dom.xpath('//input[@name="__VIEWSTATE"]/@value')[0]
    viewgen = dom.xpath('//input[@name="__VIEWSTATEGENERATOR"]/@value')[0]
    eventval = dom.xpath('//input[@name="__EVENTVALIDATION"]/@value')[0]

    formdata = {
        "__EVENTTARGET": "redirect",
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": viewgen,
        "__EVENTVALIDATION": eventval,
    }

    response = session.post(response.url, data=formdata, headers=headers)
    response = session.get(response.url, headers=headers)
    dom = etree.HTML(response.text)
    viewstate = dom.xpath('//input[@name="__VIEWSTATE"]/@value')[0]
    viewgen = dom.xpath('//input[@name="__VIEWSTATEGENERATOR"]/@value')[0]
    eventval = dom.xpath('//input[@name="__EVENTVALIDATION"]/@value')[0]

    formdata = {
        "__EVENTTARGET": "btnPageLoad",
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": viewgen,
        "__EVENTVALIDATION": eventval,
        "hdnLoaded": "true",
        "hdnTimeZone": "Europe/Madrid",
    }
    hdr = {"Content-Type": "application/x-www-form-urlencoded"}
    response = session.post(response.url, data=formdata, headers=hdr)
    response = session.get(response.url, headers=headers)
    dom = etree.HTML(response.text)
    viewstate = dom.xpath('//input[@name="__VIEWSTATE"]/@value')[0]
    viewgen = dom.xpath('//input[@name="__VIEWSTATEGENERATOR"]/@value')[0]
    eventval = dom.xpath('//input[@name="__EVENTVALIDATION"]/@value')[0]

    all_locations = []
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=200,
        max_search_results=None,
    )
    for code in all_codes:
        formdata = {
            "__VIEWSTATE": viewstate,
            "__VIEWSTATEGENERATOR": viewgen,
            "__EVENTVALIDATION": eventval,
            "txtLocationQuery": code,
            "cmbWithinDistance": "200",
            "btnLoadLocations": "Search",
        }

        me = MultipartEncoder(fields=formdata)
        me_boundary = me.boundary[2:]
        me_body = me.to_string()
        headers = {
            "Content-Type": "multipart/form-data; charset=utf-8; boundary="
            + me_boundary
        }

        response = session.post(response.url, data=me_body, headers=headers)
        dom = etree.HTML(response.text)
        viewstate = dom.xpath('//input[@name="__VIEWSTATE"]/@value')[0]
        viewgen = dom.xpath('//input[@name="__VIEWSTATEGENERATOR"]/@value')[0]
        eventval = dom.xpath('//input[@name="__EVENTVALIDATION"]/@value')[0]

        all_locations += dom.xpath('//div[@class="LocationDiv"]')

    for poi_html in all_locations:
        store_url = "<MISSING>"
        location_name = poi_html.xpath('.//div[@class="StudioInfoClass"]/b/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = poi_html.xpath('.//div[@class="StudioInfoClass"]/text()')
        street_address = raw_address[0]
        city = raw_address[1].split(", ")[0]
        state = raw_address[1].split(", ")[-1].split()[0]
        zip_code = raw_address[1].split(", ")[-1].split()[-1]
        phone = raw_address[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"

        item = [
            DOMAIN,
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
        check = f"{location_name} {street_address}"
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
