# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
import re
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import httpx

website = "mortonsgrille.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.mortonsgrille.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def validhour(x):
    if (
        ("AM" in x.upper() and "PM" in x.upper())
        or (re.search("\\d *[AP]M", x.upper()))
        or ("DAILY" in x.upper())
        or ("M" in x.upper() and ":" in x.upper())
        or ("TU" in x.upper() and ":" in x.upper())
        or ("WED" in x.upper() and ":" in x.upper())
        or ("TH" in x.upper() and ":" in x.upper())
        or ("F" in x.upper() and ":" in x.upper())
        or ("SA" in x.upper() and ":" in x.upper())
        or ("SU" in x.upper() and ":" in x.upper())
        or ("～" in x.upper())
        or ("-" in x.upper())
    ):

        if (
            "JAN" in x.upper()
            or "FEB" in x.upper()
            or "MAR" in x.upper()
            or "APR" in x.upper()
            or "MAY" in x.upper()
            or "JUN" in x.upper()
            or "JUL" in x.upper()
            or "AUG" in x.upper()
            or "SEP" in x.upper()
            or "OCT" in x.upper()
            or "NOV" in x.upper()
            or "DEC" in x.upper()
            or "HOLIDAY" in "".join(x.upper()[:7])  # Extra check for Holiday
            or "E-MAIL." in x.upper()
            or "E-MAIL:" in x.upper()
            or "PRIOR TO YOUR VISIT." in x.upper()
            or "IN-PERSON" in x.upper()
            or "IN-STORE" in x.upper()
        ):
            return False
        return True
    return False


def get_latlng(map_link):
    if "z/data" in map_link:
        lat_lng = map_link.split("@")[1].split("z/data")[0]
        latitude = lat_lng.split(",")[0].strip()
        longitude = lat_lng.split(",")[1].strip()
    elif "ll=" in map_link:
        lat_lng = map_link.split("ll=")[1].split("&")[0]
        latitude = lat_lng.split(",")[0]
        longitude = lat_lng.split(",")[1]
    elif "!2d" in map_link and "!3d" in map_link:
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
    elif "/@" in map_link:
        latitude = map_link.split("/@")[1].split(",")[0].strip()
        longitude = map_link.split("/@")[1].split(",")[1].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here
    search_urls_list = [
        "https://www.mortonsgrille.com/locations/",
        "https://www.mortonsgrille.com/locations/international.asp",
    ]
    timeout = httpx.Timeout(120.0, connect=120.0)

    with SgRequests(
        dont_retry_status_codes=([404]), timeout_config=timeout, verify_ssl=False
    ) as session:
        for search_url in search_urls_list:
            search_res = session.get(search_url, headers=headers)

            search_sel = lxml.html.fromstring(search_res.text)
            countries = search_sel.xpath("//section/div/div")
            if (
                search_url
                == "https://www.mortonsgrille.com/locations/international.asp"
            ):
                countries = search_sel.xpath(
                    '//section//div[@style="float:left; width:300px;"]'
                )

            for country in countries:

                locator_domain = website
                locations = country.xpath(".//h4")

                for no, location in enumerate(locations, 1):

                    page_url = (
                        "https://www.mortonsgrille.com/locations/"
                        + "".join(location.xpath("./a/@href")).strip()
                    ).strip()
                    page_url = page_url.replace("#", "").strip()
                    log.info(page_url)

                    page_url = page_url.replace("//locations", "")
                    location_name = location.xpath(".//text()")[0].strip()
                    if (
                        location_name == "HOURS OF OPERATION"
                        or location_name == "MANAGERS"
                    ):
                        continue
                    store_info = list(
                        filter(
                            str,
                            [
                                x.strip()
                                for x in country.xpath(
                                    f"./p[count(./preceding-sibling::h4)={no}]//text()"
                                )
                            ],
                        )
                    )
                    if (
                        store_info[-1]
                        .upper()
                        .replace("TEL:", "")
                        .strip()
                        .replace("+", "")
                        .replace("-", "")
                        .replace("(", "")
                        .replace(")", "")
                        .strip()
                        .replace(" ", "")
                        .strip()
                        .isdigit()
                    ):
                        raw_address = " ".join(store_info[:-1]).replace("\n", " ")
                        phone = store_info[-1].upper().replace("TEL:", "").strip()

                    else:
                        raw_address = " ".join(store_info).replace("\n", " ")
                        phone = "<MISSING>"
                    formatted_addr = parser.parse_address_intl(raw_address)
                    street_address = formatted_addr.street_address_1
                    if formatted_addr.street_address_2:
                        street_address = (
                            street_address + ", " + formatted_addr.street_address_2
                        )

                    city = formatted_addr.city
                    state = formatted_addr.state
                    zip = formatted_addr.postcode

                    country_code = country.xpath("./h2/text()")[0].strip()
                    store_number = "<MISSING>"

                    location_type = "<MISSING>"

                    if page_url == search_url:
                        hours_of_operation = "<MISSING>"
                        latitude, longitude = "<MISSING>", "<MISSING>"
                    else:
                        store_res = session.get(page_url, headers=headers)
                        store_sel = lxml.html.fromstring(store_res.text)

                        hours = list(
                            filter(
                                str,
                                [
                                    x.strip()
                                    for x in store_sel.xpath(
                                        "//h5[text()='Hours of Operation']/following-sibling::p/text()"
                                    )
                                ],
                            )
                        )
                        hours = list(filter(validhour, hours))

                        hours_of_operation = (
                            "; ".join(hours)
                            .replace("; :", ":")
                            .strip()
                            .encode("ascii", "replace")
                            .decode("utf-8")
                            .replace("?", "-")
                            .strip()
                            .replace("---", "-")
                            .strip()
                        )

                        map_link = "".join(
                            store_sel.xpath('//a[contains(@href,"maps")]/@href')
                        )

                        if not map_link:
                            map_link = "".join(
                                store_sel.xpath('//iframe[contains(@src,"maps")]/@src')
                            )

                        latitude, longitude = get_latlng(map_link)

                    if location_name == "Shenzhen, China":
                        street_address = "5033 Yitian Road"

                    yield SgRecord(
                        locator_domain=locator_domain,
                        page_url=page_url,
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zip,
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
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
