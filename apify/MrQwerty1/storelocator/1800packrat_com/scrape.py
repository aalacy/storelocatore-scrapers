import json
from lxml import html
from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

logger = SgLogSetup().get_logger("1800packrat_com")


DOMAIN = "https://www.1800packrat.com"
URL_LOCATION = "https://www.1800packrat.com/locations"
MISSING = "<MISSING>"


headers_custom_for_location_url = {
    "authority": "www.1800packrat.com",
    "method": "GET",
    "path": "/locations",
    "scheme": "https",
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "upgrade-insecure-requests": "1",
}

session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)


def get_urls():
    geo = dict()
    urls = []
    r = session.get(
        "https://www.1800packrat.com/locations",
        headers=headers_custom_for_location_url,
        timeout=180,
    )
    tree = html.fromstring(r.text)
    logger.info(f"Raw Page Source: {r.text}")
    r_text = r.text
    test_incapsula = r_text.split("div")

    if len(test_incapsula) > 2:
        text = (
            "".join(tree.xpath("//script[contains(text(), 'markers:')]/text()"))
            .split("markers:")[1]
            .split("]")[0]
            .strip()[:-1]
            + "]"
        )
        js = json.loads(text)
        for j in js:
            slug = j.get("Link")
            url = f"{DOMAIN}{slug}"
            urls.append(url)
            lat = j.get("Latitude") or MISSING
            lng = j.get("Longitude") or MISSING
            geo[slug] = {"lat": lat, "lng": lng}
            logger.info(f"Latitude & Longitude: {geo}")

        return urls, geo
    else:
        raise Exception(
            'Incapsula is active - Please try with residential proxy: "{}"'.format(
                r_text
            )
        )


def fetch_data():
    s = set()
    urls, geo = get_urls()
    logger.info(f"Number of Page URLs: {len(urls)}")
    for pnum, purl in enumerate(urls):
        logger.info(f"Pulling the data from {pnum}: {purl}")
        slug2 = purl.replace(DOMAIN, "")
        headers_custom_with_url_path = {
            "authority": "www.1800packrat.com",
            "method": "GET",
            "path": slug2,
            "scheme": "https",
            "accept": "application/json, text/plain, */*",
            "referer": "https://www.1800packrat.com/locations",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
            "upgrade-insecure-requests": "1",
        }
        r = session.get(purl, headers=headers_custom_with_url_path, timeout=180)
        tree = html.fromstring(r.text, "lxml")
        r_text = r.text
        test_incapsula = r_text.split("div")
        logger.info(f"Page Source: {r_text}")
        if len(test_incapsula) > 2:
            logger.info("Incapsula is not active yet")
            page_url = purl

            # Make sure Duplicates removed
            if page_url in s:
                continue
            s.add(page_url)

            location_name = "".join(tree.xpath("//h1/text()")).strip()
            country_code = "US"
            store_number = MISSING
            latitude = geo[slug2].get("lat")
            longitude = geo[slug2].get("lng")
            location_type = MISSING
            hours_of_operation = (
                ";".join(
                    tree.xpath("//p[contains(text(), 'CUSTOMER SERVICE HOURS')]/text()")
                )
                .replace("\n", "")
                .replace("CUSTOMER SERVICE HOURS;", "")
                or MISSING
            )

            lines = tree.xpath(
                "//p[contains(text(), 'CUSTOMER SERVICE HOURS')]/preceding-sibling::p"
            )
            for l in lines:
                raw_line = l.xpath(".//text()")
                raw_line = list(filter(None, [li.strip() for li in raw_line]))
                line = raw_line
                logger.info(f"Addressline Raw: {line}")
                street_address = ", ".join(line[:-2])
                phone = line[-1]
                line = line[-2]
                city = line.split(",")[0].strip()
                line = line.split(",")[1].strip()
                state = line.split()[0]
                try:
                    postal = line.split()[1]
                except IndexError:
                    postal = MISSING
                raw_address = ", ".join(raw_line[:-1])
                raw_address = raw_address if raw_address else MISSING
                logger.info(f"Raw Address: {raw_address}")
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=postal,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                    raw_address=raw_address,
                )
            else:
                raise Exception(
                    'Incapsula is active - Please try with residential proxy: "{}"'.format(
                        r_text
                    )
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
