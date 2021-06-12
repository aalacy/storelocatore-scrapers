from sgrequests import SgRequests
from sglogging import SgLogSetup
import csv
from lxml import html
import re
from tenacity import retry
from tenacity import stop_after_attempt
import time

logger = SgLogSetup().get_logger(logger_name="autozone_com")
locator_domain_url = " https://www.autozone.com"
MISSING = "<MISSING>"

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    "cookie": "cookie: preferedstore=2205; bm_sz=D5E0F8DDC7E6E58D6BF4559CFD87E184~YAAQlQ8kF85XRc94AQAAG21d4gu9YjnNdFI6t91XRypE1qPo9G0Qrm7NZilDO1Rq8f72u+BxpM2v7hjBuyqS6OEH1zw6aKyulYyKgbA7ksGkVr+xtYGADT2kMszIupkGSvKgNqcLZxGPSjPNm4Omh4X58Vaq4PeNkiHsoHhYsV4AEB3GicLABIFQqecHrRcgtsI=; TLTSID=45afae7cd3f015e1950100e0ed6a79aa; TLTUID=45afae7cd3f015e1950100e0ed6a79aa; ak_bmsc=EF73E1921CB827DCB2E966456E2DD79F~000000000000000000000000000000~YAAQlQ8kF9VXRc94AQAADnRd4gv19zD36KApcoKLWRv4/VvkLR9+kYs1rXeUGzKKN45h1+3S0yHjjhwKYtgRgaPYETYUoyhpx3XbozQE87nnZaAGrEVHWXnm61iVb0SSr8Bltn+YBf6rJ0cPiHp3rNgAJeGj91AMpUqGdxPCQCkfil1ZT/WEXAbVtsD1bFG4eO0uBkjCXFhruW7s7CErAozhJiuNE2fTOMnhyrQETyjfapi/90jUjwvC3xeoArjysip69W9exY7FPncTPAW3QGQE+Yyoi7vV3+au6dYcE9vu5AthmQM86g6QahJpskmzUCyO+umicb0SIVXt5okGHGdI3FhXhbQRkYraUMySkxh9kbLIQRQmSUBEBAeEXiGqN6neJspx/RFDRX40; rewardsId=; JSESSIONID=BWY5nRnFGeVm3CL2-EHlRonNiib6qOKa6jjjixxx.pr-camaro2-xl07-EStoreWS03; WWW-WS-ROUTE=ffffffff09c20ebd45525d5f4f58455e445a4a421730; AKA_A2=A; bm_mi=942C695E21B04C47664A156BF16FB626~BMEpkRk35x3f2TZrFPXxKOifXX+HVkRRMCFTggVHRqr0JnopCfalcC29talGavkzVxileSt81IuFG9dd/GVU2R6FzPdpy6A6kMykF/JABt9n3YLaodY6pouH0jVHDdEh4vb/auj+KR2iCDf1u4l1q4xasJRzwTCHlefZuLSlNrSA5mzr+2kJ9SauDP0o8ogQgZ+OqnOWcQPO4HQE8bfGOIJAmrujop0cRJhqLwKMmDk=; profileId=19308656019; cartProductPartIds=; cartProductSkus=; cartProductTitles=; cartProductVendors=; cartUnitPrice=; cartDiscountPriceList=; prevUrlRouteValue=/; _abck=6E710B00C3C2F3E48C4D20B035973642~0~YAAQX0ofRRHaRdB4AQAA9reZ4gUZPuRQsAVl1AmWKqBqP5VZ33EoZp7oHxpT/VnBlghGCUvRorrnTnNUOH3cVFw/8UvK4qWl+ouIQf4u++3darhHtW9G+H3C0dHpX/5D37gRmnjQpKqLWZlQvO0gFMZckYLP/pFsw09WIdf0pdt2bnuFPs8yDIce6vJC3mrQPEQU9UAPLth0Z+Y576BETphcftJLEQncJbCYujDdBo6wPa+aJhRl+UU+SAUNf+nJMxWutO/svRqy4qasNGNUhL2gctuWsgsNNaC+nvjgQ5NErl8ICO5FFe3BXeWdMxqC4FzKel3YtTsV3jvg3c8148anj1gp19KgorPyvAmpy0JDafjiqBIzVDZLB1U8skCYAQMpnDh0WuizHVN2yxhbNCj8hm4pZZ3HPw==~-1~-1~-1; userType=3; nddMarket=LAS, NV; nddHub=2207; nddStore=6960; bm_sv=654B9C44734C3836E4F9F85279273256~GA1yVGXwqoDT+oRblV04fc9UR2AwEFe41ES3gLUdjRiI+eZ6s6tAjRYqBpgkEDFJXAoQOkbEEn6cJqwrbm8gFbZNPezqJEq1W2dVNt0EuN4UyYqOPdsCNFQ0H2mOSAw6qVJpF/Q0bDpsi0ruXI8Psu1CUzpA6lJ7Tg4oiNGBM7s=",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
}
session = SgRequests()

FIELDS = [
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


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(FIELDS)
        for row in data:
            writer.writerow(row)


@retry(stop=stop_after_attempt(10))
def get_result(url, headers):
    global session
    try:
        return session.get(url, headers=headers)
    except:
        session = SgRequests()
        raise


url_sitemap_main = "https://www.autozone.com/locations/sitemap.xml"
r = session.get(url_sitemap_main, headers=headers, timeout=500)
datar = html.fromstring(bytes(r.text, encoding="utf8"))
url_sub_sitemap = datar.xpath("//sitemap/loc/text()")
logger.info(f"Sitemap URLs: {len(url_sub_sitemap)}")


def get_all_raw_store_urls():
    urls_part1_and_part2 = []
    for url_part in url_sub_sitemap:
        r0 = session.get(url_part, headers=headers, timeout=500)
        datar0 = html.fromstring(bytes(r0.text, encoding="utf8"))
        logger.info(f"Scraping All Store URLs from: {url_part} ")
        urls_0 = datar0.xpath("//url/loc/text()")
        urls_part1_and_part2.extend(urls_0)
    return urls_part1_and_part2


def get_filtered_urls():
    url_results = get_all_raw_store_urls()
    pattern_tx1 = r"\/[batteries, brakes]\w+.html"
    pattern_tx2 = r"((?=.*\d).+)"
    url_tx_reg1 = []
    url_tx_reg2 = []
    for i in url_results:
        reg_tx1 = re.findall(pattern_tx1, i)
        if not reg_tx1:
            url_tx_reg1.append(i)
    for j in url_tx_reg1:
        reg_tx2 = re.findall(pattern_tx2, j)
        if reg_tx2:
            url_tx_reg2.append(j)
    url_tx_reg2 = [
        url for url in url_tx_reg2 if "/es/" not in url
    ]  # Remove spanish language based urls
    return url_tx_reg2


def get_hoo(hoo_details):
    hoo = []
    for td in hoo_details:
        week_date = td.xpath("./td/text()")
        week_date = "".join(week_date)
        logger.info(f"Week Day: {week_date}")
        date_time = td.xpath("./td/span/span/text()")
        date_time = " ".join(date_time)
        logger.info(f"Week Day Time: {date_time}")
        hoo_per_day = f"{week_date} {date_time}"
        hoo.append(hoo_per_day)
    hoo = "; ".join(hoo)
    logger.info(f"Hours of Operation: {hoo}")

    if hoo:
        return hoo
    else:
        return MISSING


def fetch_data():
    global session
    items = []
    all_store_urls = get_filtered_urls()
    logger.info(f"Store URLs count: {len(all_store_urls)}")
    for idx, url in enumerate(all_store_urls):
        r = get_result(url, headers=headers)
        time.sleep(5)
        data_raw = html.fromstring(r.text, "lxml")
        logger.info(f"Pulling the Data from: {idx} <<:>> {url}")
        locator_domain = locator_domain_url
        page_url = url if url else MISSING

        location_name = data_raw.xpath('//h1[@class="c-location-title"]/span/text()')
        location_name = " ".join(location_name)
        logger.info(f"Location Name: {location_name}")

        street_address = data_raw.xpath('//meta[@itemprop="streetAddress"]/@content')
        street_address = "".join(street_address).strip()
        street_address = street_address if street_address else MISSING
        logger.info(f"street_address: {street_address}")

        city = data_raw.xpath('//span[@itemprop="addressLocality"]/text()')
        city = "".join(city).strip()
        city = city if city else MISSING
        logger.info(f"City Name: {city}")

        state = data_raw.xpath('//abbr[@itemprop="addressRegion"]/text()')
        state = "".join(state).strip()
        state = state if state else MISSING
        logger.info(f"State Name: {state}")

        zipcode = data_raw.xpath('//span[@itemprop="postalCode"]/text()')
        zipcode = "".join(zipcode).strip()
        zip = zipcode if zipcode else MISSING
        logger.info(f"Zip: {zip}")

        country_code = "US"
        try:
            store_number = location_name.split("#")[1]
        except:
            store_number = MISSING
        logger.info(f"Store Number: {store_number}")

        phone = data_raw.xpath('//span[@itemprop="telephone"]/text()')
        phone = "".join(phone).strip()
        phone = phone if phone else MISSING
        logger.info(f"Phone Number: {phone}")

        location_type_xpath = '//a[contains(@data-ya-track, "servicesavail")]/text()'
        location_type = data_raw.xpath(location_type_xpath)
        location_type = ", ".join(location_type).strip()
        location_type = location_type if location_type else MISSING
        logger.info(f"Location Type: {location_type}")

        latitude_xpath = '//meta[@itemprop="latitude"]/@content'
        latitude = data_raw.xpath(latitude_xpath)
        latitude = "".join(latitude).strip()
        latitude = latitude if latitude else MISSING
        logger.info(f"Latitude: {latitude}")

        longitude_xpath = '//meta[@itemprop="longitude"]/@content'
        longitude = data_raw.xpath(longitude_xpath)
        longitude = "".join(longitude).strip()
        longitude = longitude if longitude else MISSING
        logger.info(f"Longitude: {longitude}")

        hoo_details_xpath = '//table[@class="c-location-hours-details"]/tbody/tr'
        hoo_details = data_raw.xpath(hoo_details_xpath)
        hours_of_operation = get_hoo(hoo_details)
        row = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            zip,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]

        items.append(row)
    return items


def scrape():
    logger.info("Scraping Started!")
    data = fetch_data()

    logger.info(f" Scraping Finished | Total Store Count:{len(data)}")
    write_output(data)


if __name__ == "__main__":
    scrape()
