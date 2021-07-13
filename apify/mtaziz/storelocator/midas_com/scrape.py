from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup
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


logger = SgLogSetup().get_logger("midas_com")
MISSING = "<MISSING>"
DOMAIN = "https://www.midas.com"
SITEMAP_URL = "https://www.midas.com/tabid/697/default.aspx"
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
}

session = SgRequests().requests_retry_session(retries=0)


def get_all_store_url():
    r1 = session.get(SITEMAP_URL, headers=headers)
    d1 = html.fromstring(r1.text, "lxml")
    us_state_urls = d1.xpath(
        '//div[h2[contains(text(), "Midas Stores - United States")]]/ul/li/a/@href'
    )
    logger.info(f"total count for the USA: {us_state_urls}")
    us_state_urls = [f"{DOMAIN}{url}" for url in us_state_urls]
    ca_state_urls = d1.xpath(
        '//div[h2[contains(text(), "Midas Stores - Canada")]]/ul/li/a[contains(@href, "sitemap.aspx?country=CA")]/@href'
    )
    ca_state_urls = [f"{DOMAIN}{url}" for url in ca_state_urls]
    us_ca_state_urls = us_state_urls + ca_state_urls
    us_ca_store_urls = []
    for u in us_ca_state_urls:
        logger.info(f"Pulling the store URLs from: {u}")
        r3 = session.get(u, headers=headers)
        d3 = html.fromstring(r3.text, "lxml")
        store_url_list = d3.xpath(
            '//li/a[contains(@class, "link") and contains(@href, "store.aspx")]/@href'
        )
        store_url_list = [f"{DOMAIN}{sul}" for sul in store_url_list]
        logger.info(f"Found: {len(store_url_list)}")
        us_ca_store_urls.extend(store_url_list)
    us_ca_store_urls = list(set(us_ca_store_urls))

    return us_ca_store_urls


def fetch_data():
    # Your scraper here
    all_store_urls = get_all_store_url()
    identities = set()
    for idx, store_url in enumerate(all_store_urls):
        # for idx, store_url in enumerate(all_store_urls[0:20]):
        logger.info(f"Pulling the data from: {store_url} ")
        store_number = store_url.split("shopnum=")[-1].split("&dmanum")[0]
        get_store_details_by_shopnum = (
            "https://www.midas.com/shop/getstorebyshopnumber?shopnum={}"
        )
        poi = session.get(
            get_store_details_by_shopnum.format(store_number), headers=headers
        ).json()

        location_name = poi["Name"]
        location_name = location_name if location_name else "<MISSING>"
        page_url = store_url
        locator_domain = DOMAIN
        street_address = poi["Address"]
        street_address = street_address if street_address else "<MISSING>"

        city = poi["City"]
        city = city if city else "<MISSING>"

        state = poi["State"]
        state = state if state else "<MISSING>"

        zip_postal = poi["ZipCode"]
        zip_postal = zip_postal if zip_postal else "<MISSING>"

        country_code = poi["Country"]
        country_code = country_code if country_code else "<MISSING>"

        store_number = poi["ShopNumber"]
        store_number = store_number if store_number else "<MISSING>"

        phone = poi["PhoneNumber"]
        phone = phone if phone else "<MISSING>"

        location_type = MISSING
        latitude = poi["Latitude"]
        latitude = latitude if latitude else "<MISSING>"

        longitude = poi["Longitude"]
        longitude = longitude if longitude else "<MISSING>"
        if store_number in identities:
            continue
        identities.add(store_number)
        hoo = []
        for i in poi["GroupDaysList"]:
            dayhours = i["DayLabel"] + " " + i["HoursLabel"]
            hoo.append(dayhours)
        hours_of_operation = "; ".join(hoo)
        hours_of_operation = hours_of_operation if hours_of_operation else MISSING
        raw_address = MISSING
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
    logger.info(" Scraping Started")
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
