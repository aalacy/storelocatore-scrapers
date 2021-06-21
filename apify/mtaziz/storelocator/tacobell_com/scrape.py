from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from lxml import html

import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("tacobell_com")
MISSING = "<MISSING>"
DOMAIN = "https://www.tacobell.com"
URL_LOCATION = "https://locations.tacobell.com/"

headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
}


def get_page_urls():
    session = SgRequests()
    r1 = session.get(URL_LOCATION, headers=headers)
    sel1 = html.fromstring(r1.text, "lxml")
    state_urls = sel1.xpath('//a[contains(@data-ya-track, "directory_links")]/@href')
    state_urls = [f"{URL_LOCATION}{url}" for url in state_urls]
    city_urls_2 = []
    page_urls_1 = []
    for idx2, surl in enumerate(state_urls):
        logger.info(f"Pulling from the State: {idx2}: {surl} ")
        r2 = session.get(surl, headers=headers)
        sel2 = html.fromstring(r2.text, "lxml")
        city_urls = sel2.xpath('//a[span[@class="Directory-listLinkText"]]/@href')
        # Identify if the URL is city-based URL or page URL
        for url in city_urls:
            url_s = url.split("/")
            if len(url_s) == 2:
                city_urls_2.append(url)
            else:
                page_urls_1.append(url)

    city_urls_2 = [f"{URL_LOCATION}{url}" for url in city_urls_2]
    page_urls_1 = [f"{URL_LOCATION}{url}" for url in page_urls_1]
    for idx3, curl in enumerate(city_urls_2[0:]):
        logger.info(f"Crawling at {idx3} out of {len(city_urls_2)} cities || {curl} ")
        r3 = session.get(curl, headers=headers)
        sel3 = html.fromstring(r3.text, "lxml")
        page_urls_from_city_url = sel3.xpath('//a[@data-ya-track="visit_site"]/@href')
        page_urls_from_city_url = [
            f'{URL_LOCATION}{url.replace("../", "")}' for url in page_urls_from_city_url
        ]
        page_urls_1.extend(page_urls_from_city_url)
    logger.info(f"Total Store Count: {len(page_urls_1)}")
    return page_urls_1


def fetch_data():
    all_urls = get_page_urls()
    session = SgRequests()
    s = set()
    for idx4, url in enumerate(all_urls[0:]):
        r4 = session.get(url, headers=headers)
        sel4 = html.fromstring(r4.text, "lxml")
        locator_domain = DOMAIN
        page_url = url
        logger.info(f"Pulling the data from {idx4} of {len(all_urls)}: {url} ")
        location_name = ""

        street_address = sel4.xpath(
            '//div[@class="Core-address"]/address/div/span[@class="c-address-street-1"]/text()'
        )
        street_address = "".join(street_address)
        street_address = street_address if street_address else MISSING

        city = sel4.xpath(
            '//div[@class="Core-address"]/address/div/span[@class="c-address-city"]/text()'
        )
        city = "".join(city)
        city = city if city else MISSING

        state = sel4.xpath(
            '//div[@class="Core-address"]/address/div/abbr[@class="c-address-state"]/text()'
        )
        state = "".join(state)
        state = state if state else MISSING

        zip_postal = sel4.xpath(
            '//div[@class="Core-address"]/address/div/span[@class="c-address-postal-code"]/text()'
        )
        zip_postal = "".join(zip_postal)
        zip_postal = zip_postal if zip_postal else MISSING

        country_code = sel4.xpath('//address[@itemprop="address"]/@data-country')
        country_code = "".join(country_code)
        country_code = country_code if country_code else MISSING
        logger.info(
            f"Street Address: {street_address} | City: {city} | State: {state} | Zip: {zip_postal} | Country: {country_code}"
        )

        store_number = sel4.xpath('//div[@id="Core"]/@data-code')
        store_number = "".join(store_number)

        if store_number in s:
            continue
        s.add(store_number)
        store_number = store_number if store_number else MISSING

        phone = sel4.xpath(
            '//div[@class="Core-phones Core-phones--single"]/div/div/div[@itemprop="telephone"]/text()'
        )
        phone = "".join(phone)
        phone = phone if phone else MISSING

        location_type = MISSING

        if store_number:
            location_name = f"Taco Bell {store_number}"
        else:
            location_name = "Taco Bell"

        latitude = sel4.xpath('//meta[@itemprop="latitude"]/@content')
        latitude = "".join(latitude)
        latitude = latitude if latitude else MISSING

        longitude = sel4.xpath('//meta[@itemprop="longitude"]/@content')
        longitude = "".join(longitude)
        longitude = longitude if longitude else MISSING
        logger.info(f"(Latitude, Longitude): ({latitude}, {longitude})")

        hours_of_operation = ""
        hoo = []
        c_hours_details = sel4.xpath(
            '//div[@class="Core-hours"]/div[h2[contains(text(), "Dine-In Hours")]]/div/table[@class="c-hours-details"]/tbody/tr'
        )
        for tr in c_hours_details:
            hrs_details = tr.xpath(".//td//text()")
            hrs_details = " ".join(hrs_details)
            hrs_details = hrs_details.replace("  -  ", " - ")
            hoo.append(hrs_details)
        hours_of_operation = "; ".join(hoo)
        hours_of_operation = hours_of_operation if hours_of_operation else MISSING
        logger.info(f"Hours of Operation: {hours_of_operation}")
        raw_address = ""
        raw_address = raw_address if raw_address else MISSING

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
