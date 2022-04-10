# -*- coding: utf-8 -*-

from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import ssl
from sgpostal.sgpostal import parse_address_intl
import os

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


DOMAIN = "barbour.com"
logger = SgLogSetup().get_logger("barbour_com")  # noqa
MISSING = SgRecord.MISSING

hd_it = {
    "referer": "https://www.barbour.com/storelocator",
    "accept": "*/*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}

DEFAULT_PROXY_URL = "https://groups-RESIDENTIAL,country-it:{}@proxy.apify.com:8000/"


def set_proxies():
    if "PROXY_PASSWORD" in os.environ and os.environ["PROXY_PASSWORD"].strip():

        proxy_password = os.environ["PROXY_PASSWORD"]
        url = (
            os.environ["PROXY_URL"] if "PROXY_URL" in os.environ else DEFAULT_PROXY_URL
        )
        proxy_url = url.format(proxy_password)
        proxies = {
            "https://": proxy_url,
        }
        return proxies
    else:
        return None


def get_page_url(url_key, cc):
    page_url = ""
    if url_key:
        if "US" in cc:
            page_url = "https://www.barbour.com/us/storelocator/" + url_key
        elif "GB" in cc:
            page_url = "https://www.barbour.com/uk/storelocator/" + url_key
        else:
            page_url = "https://www.barbour.com/storelocator/" + url_key
    else:
        page_url = MISSING
    if "https://www.barbour.com/storelocator/-" == page_url:
        page_url = "https://www.barbour.com/storelocator"
    return page_url


def get_street_address(sta):
    street_add = ""
    if sta or sta is not None:
        street_add = sta.replace("?", "").strip()
    else:
        street_add = ""

    if street_add == "-":
        street_add = ""

    if street_add:
        street_add = " ".join(street_add.replace("\r\n", " ").split())

    if street_add and street_add.startswith(","):
        street_add = street_add[1:].strip()
    return street_add


def parse_street_address_round2(raw_add):
    pai = parse_address_intl(raw_add)
    sta1 = pai.street_address_1
    sta2 = pai.street_address_2
    sta = ""
    if sta1 is not None and sta2 is None:
        sta = sta1
    elif sta1 is None and sta2 is not None:
        sta = sta2
    elif sta1 is not None and sta2 is not None:
        sta = sta1 + ", " + sta2
    else:
        sta = "<MISSING>"
    return sta


def parse_street_address_round2_jp(raw_add):
    pai = parse_address_intl(raw_add)
    sta1 = pai.street_address_1
    sta2 = pai.street_address_2
    sta = ""
    if sta1 is not None and sta2 is None:
        sta = sta1
    elif sta1 is None and sta2 is not None:
        sta = sta2
    elif sta1 is not None and sta2 is not None:
        sta = sta1 + ", " + sta2
    else:
        sta = "<MISSING>"
    return sta


def fetch_data():
    # NOTE: The geo location is important factor while accessing store Locator URL

    # For Example, if we happen to access the website from the US-based
    # location such as New York, the website is likely to redirect to it's respective
    # Store Locator URL, https://www.barbour.com/us/storelocator.

    # If we happen to access it from London, UK
    # it will redirect to https://www.barbour.com/uk/storelocator.

    # If we happen to access from other country like Italy, then
    # Store Locator URL would be https://www.barbour.com/storelocator

    # Considering above, the proxy is set to Italy so that it would return
    # all the stores across the world

    # Proxy country must be passed with Italy ( it ) otherwise,
    # we may not get all the stores
    proxy_country_it = "it"
    locator_url_global = "https://www.barbour.com/storelocator"
    locator_url_us = "https://www.barbour.com/us/storelocator"
    s_us = SgRequests(proxy_country=proxy_country_it)
    s_us.proxies = set_proxies()

    r = s_us.get(locator_url_global)
    response_url = str(r.url)

    if response_url == locator_url_us:
        logger.info(f"locator url found to be based on the US : {response_url}")
        raise Exception("Please run with proxy based on the location of Italy")
    else:
        logger.info(f"Response Locator URL: {response_url}")
        logger.info(
            "<<< Proxy location found to be non-US and non-UK based:) Happy! >>>"
        )
        with SgRequests(proxy_country=proxy_country_it) as session_it:
            page_url = ""
            location_name = ""
            street_address = ""
            city = ""
            state = ""
            zip_code = ""
            country_code = ""
            store_number = ""
            phone = ""
            location_type = ""
            latitude = ""
            longitude = ""
            hours_of_operation = ""
            raw_address = ""

            session_it.proxies = set_proxies()
            payload_it = "lat=45.4642035&lng=9.189982&radius=50000&mapId=amlocator-map-canvas6203f16fd942a&storeListId=amlocator_store_list6203f16fd967b&product=0&category=0&attributes%5B0%5D%5Bname%5D=2&attributes%5B0%5D%5Bvalue%5D=&attributes%5B1%5D%5Bname%5D=3&attributes%5B1%5D%5Bvalue%5D=&attributes%5B2%5D%5Bname%5D=4&attributes%5B2%5D%5Bvalue%5D=&attributes%5B3%5D%5Bname%5D=5&attributes%5B3%5D%5Bvalue%5D="
            api_url_it = "https://www.barbour.com/amlocator/index/ajax/"
            rit = session_it.post(
                api_url_it, data=json.dumps(payload_it), headers=hd_it
            )
            data_it = json.loads(rit.text)["items"]
            for idx, poi in enumerate(data_it[0:]):
                country_code = poi["country"] if poi["country"] else ""
                if country_code == "JP":
                    continue
                else:
                    location_name = poi["name"]
                    logger.info(
                        f"<< Location Name: {location_name}, IDX: {idx} >> "
                    )  # noqa

                    # Page URL bassed on countries ISO code
                    page_url = get_page_url(poi["url_key"], country_code)

                    # Street Address
                    street_address = get_street_address(poi["address"])

                    # City
                    city = poi["city"]
                    if city or city is not None:
                        city = city.replace("?", "")
                    else:
                        city = ""

                    if "???" in city:
                        city = city.replace("?", "")
                    if "." == city:
                        city = ""

                    logger.info(f"[{idx}] << Round1 City: {city} >>")  # noqa
                    state = poi["state"]
                    if state or state is not None:
                        state = state
                    else:
                        state = ""
                    if state and state.isdigit():
                        state = ""
                    zip_code = poi["zip"]
                    store_number = poi["id"]

                    phone = poi["phone"]
                    if phone or phone is not None:
                        phone = phone
                    else:
                        phone = ""
                    if phone == "-":
                        phone = ""
                    location_type = ""
                    if poi["attributes"].get("stockist_type", {}).get("option_title"):
                        location_type = ", ".join(
                            poi["attributes"]["stockist_type"]["option_title"]
                        )
                    latitude = poi["lat"]
                    if latitude or latitude is not None:
                        latitude = latitude
                    else:
                        latitude = MISSING

                    if latitude == "0.00000000":
                        latitude = MISSING
                    longitude = poi["lng"]
                    if longitude or longitude is not None:
                        longitude = longitude
                    else:
                        longitude = MISSING

                    if longitude == "0.00000000":
                        longitude = MISSING

                    raw_address = f'{street_address}, {poi["city"]}, {poi["state"]}, {poi["zip"]}, {poi["country"]}'.strip()
                    raw_address = " ".join(raw_address.split())
                    raw_address = raw_address.replace("None,", "")
                    raw_address = raw_address.replace(", ,  .,", "")

                    addr = parse_address_intl(raw_address)
                    if not zip_code:
                        zip_code = addr.postcode
                    if not city:
                        city = addr.city
                    if not state:
                        state = addr.state

                    if phone and phone == zip_code:
                        phone = ""
                    if phone and phone == city:
                        phone = ""
                    if zip_code and "@" in zip_code:
                        zip_code = ""
                    if zip_code and zip_code == ".":
                        zip_code = ""
                    if phone and phone.startswith("-"):
                        phone = phone[1:]
                    if phone:
                        phone = (
                            phone.split("..")[0]
                            .replace("Voss", "")
                            .split("(P")[0]
                            .split("J")[0]
                            .split("Butik:")[-1]
                            .split("Inköp:")[0]
                            .replace("Butik", "")
                            .replace("Tel:", "")
                            .split("(butik")[0]
                            .split("/ 8 (800")[0]
                            .split("（バ")[0]
                            .replace("03-3567-2224", "")
                            .replace("https://www.proidee.de/", "")
                            .strip()
                        )
                        if phone.endswith("."):
                            phone = phone[:-1]
                    if city and city == "None":
                        city = ""
                    if zip_code and state:
                        zip_code = zip_code.replace(state, "").strip()
                    if street_address and city:
                        if city in street_address:
                            street_address = street_address.split(city)[0].strip()
                            if street_address.endswith(","):
                                street_address = street_address[:-1]
                    if city and city == ", , None, .,":
                        city = ""
                    if city and city == ".":
                        city = ""

                    if street_address and street_address.strip().startswith(","):
                        street_address = street_address[1:]
                    # Parsed street_address
                    street_address = parse_street_address_round2(raw_address)
                    item = SgRecord(
                        locator_domain=DOMAIN,
                        page_url=page_url,
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zip_code,
                        country_code=country_code,
                        store_number=store_number,
                        phone=phone,
                        location_type=location_type,
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=hours_of_operation,
                        raw_address=raw_address,
                    )

                    yield item


def scrape():
    logger.info("Started")  # noqa
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.LATITUDE,
                }
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
    logger.info("Finished")  # noqa
