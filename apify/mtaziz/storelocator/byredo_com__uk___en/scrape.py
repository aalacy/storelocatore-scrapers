from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import phonenumbers
import csv
from lxml import html
import re
import time
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("byredo_com__uk___en")
DOMAIN = "https://www.byredo.com"
URL_LOCATION = "https://www.byredo.com/uk_en/find-a-store"
MISSING = "<MISSING>"

headers = {
    "Connection": "keep-alive",
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
}


def get_url_for_all_countries():
    session = SgRequests()
    r = session.get(URL_LOCATION, headers=headers)
    sel = html.fromstring(r.text, "lxml")
    urls_for_all_countries = sel.xpath('//ul[@class="cms-menu"]/li/ul/li/a/@href')
    url_germany = "https://www.byredo.com/us_en/store-germany"
    urls_for_all_countries.append(url_germany)
    return urls_for_all_countries


urls_for_all_countries = get_url_for_all_countries()


def fetch_data_global():
    session = SgRequests()

    for urlnum, base_url in enumerate(urls_for_all_countries[0:]):
        if (
            "china" in base_url
            or "france" in base_url
            or "sweden" in base_url
            or "united-kingdom" in base_url
            or "united-states" in base_url
            or "store-germany" in base_url
        ):
            r = session.get(base_url, headers=headers)
            tree = html.fromstring(r.text, "lxml")
            tds = tree.xpath('//div[@class="column main"]//table/tbody')
            for idxuk, td in enumerate(tds):
                location_names = td.xpath("//tr/td/h3//descendant::text()")
                address_data = td.xpath(
                    "//tr/td//text()[count(preceding-sibling::h2)=$count]",
                    count="{}".format(idxuk),
                )
                address_data1 = " ".join(address_data)
                logger.info(f"Address Data UK: {address_data1}")
                address_data2 = address_data1.split("Map")
                address_data3 = [" ".join(i.split()) for i in address_data2 if i]
                address_data3 = [i for i in address_data3 if i]
                logger.info(f"Number of Addresses Found: {address_data3}")
                phone_numbers = ["+" + i.split("+")[-1] for i in address_data3 if i]
                logger.info(f"Phone Numbers: {idxuk}: \n{phone_numbers}")
                latlng_from_googlemap_url = td.xpath(
                    '//a[contains(text(), "Map")]/@href'
                )
                logger.info(f"latlng data: {latlng_from_googlemap_url}")
                latlng_from_googlemap_url_deduped = list(
                    dict.fromkeys(latlng_from_googlemap_url)
                )

            for idxuk1, address in enumerate(address_data3):
                logger.info(f"Parsing the address: {idxuk1}: {address}")
                address_without_phone_data = address.split("+")
                address_wpd = address_without_phone_data[0].strip()
                logger.info(f"Address without Phone data: {idxuk1}: {address_wpd}")

                address_wpd1 = address_wpd.split("Temporarily closed")[0].strip()
                paddress = parse_address_intl(address_wpd1)
                logger.info(f"Parsed Address: {paddress}")

                street_address = paddress.street_address_1 or "<MISSING>"
                logger.info(f"Street Address: {street_address}")

                city = paddress.city or "<MISSING>"
                state = paddress.state or "<MISSING>"
                zip_postal = paddress.postcode or "<MISSING>"
                locator_domain = DOMAIN
                page_url = base_url
                page_url = page_url if page_url else MISSING

                try:
                    location_name = location_names[idxuk1]
                except:
                    location_name = MISSING
                logger.info(f"Location Name: {idxuk1}: {location_name}")

                country_code = r.url.split("/")[-1]
                if country_code == "china":
                    country_code = "CH"
                if country_code == "france":
                    country_code = "FR"
                if country_code == "korea":
                    country_code = "KR"
                if country_code == "russia":
                    country_code = "RU"
                if country_code == "sweden":
                    country_code = "SE"
                if country_code == "united-arab-emirates":
                    country_code = "AE"
                if country_code == "united-kingdom":
                    country_code = "UK"
                if country_code == "united-states":
                    country_code = "US"
                if country_code == "store-germany":
                    country_code = "DE"

                store_number = "<MISSING>"
                phone = ""

                phone_data_to_be_parsed = phone_numbers[idxuk1]
                for match in phonenumbers.PhoneNumberMatcher(
                    phone_data_to_be_parsed, country_code
                ):
                    phone = phonenumbers.format_number(
                        match.number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
                    )
                phone = phone if phone else MISSING
                location_type = "<MISSING>"
                if country_code == "US":
                    if "@" in latlng_from_googlemap_url_deduped[idxuk1]:
                        latitude = (
                            latlng_from_googlemap_url_deduped[idxuk1]
                            .split("@")[1]
                            .split(",")[0]
                            or "<MISSING>"
                        )
                        longitude = (
                            latlng_from_googlemap_url_deduped[idxuk1]
                            .split("@")[1]
                            .split(",")[1]
                            or "<MISSING>"
                        )
                    else:
                        latitude = "<MISSING>"
                        longitude = "<MISSING>"
                else:
                    latitude = (
                        latlng_from_googlemap_url_deduped[idxuk1]
                        .split("@")[1]
                        .split(",")[0]
                        or "<MISSING>"
                    )
                    longitude = (
                        latlng_from_googlemap_url_deduped[idxuk1]
                        .split("@")[1]
                        .split(",")[1]
                        or "<MISSING>"
                    )
                hours_of_operation = MISSING
                logger.info(f"hours of operation raw: {hours_of_operation}")
                raw_address = address_wpd
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


def fetch_data_russia():
    session = SgRequests()
    for urlnum, base_url in enumerate(urls_for_all_countries[0:]):
        if "russia" in base_url:
            r = session.get(base_url, headers=headers)
            tree = html.fromstring(r.text, "lxml")
            tds = tree.xpath(
                '//div[@class="column main"]//div[@data-content-type="html"]'
            )
            for idx, td in enumerate(tds):
                address_data2_temp = []
                # Location Names
                location_names = td.xpath("./h3/descendant::text()")

                # Address Data
                address_data = td.xpath("./text()")
                address_data1 = [" ".join(i.split()) for i in address_data]
                address_data2 = [i for i in address_data1 if i]
                address_data2 = ", ".join(address_data2)
                address_data2_temp.append(address_data2)

                logger.info(f"Number of Addresses Found: {address_data2_temp}")

                telephone_data = td.xpath("./span/text()")
                logger.info(f"Phone Numbers: {idx}: \n{telephone_data}")

                # Latitude and longitude data
                latlng_from_googlemap_url = td.xpath(
                    '//a[contains(text(), "Map")]/@href'
                )
                logger.info(f"latlng data: {latlng_from_googlemap_url}")
                latlng_from_googlemap_url_deduped = list(
                    dict.fromkeys(latlng_from_googlemap_url)
                )

            for idx1, address in enumerate(address_data2_temp):
                address_raw = "".join(address)
                if "Russia" not in address_raw.lower():
                    address_raw = address_raw + ", " + "Russia"
                else:
                    address_raw = address_raw

                logger.info(f"Parsing the address: {idx1}: {address_raw}")

                paddress = parse_address_intl(address_raw)
                logger.info(f"Parsed Address: {paddress}")

                street_address = paddress.street_address_1 or "<MISSING>"
                logger.info(f"Street Address: {street_address}")

                city = paddress.city or "<MISSING>"
                state = paddress.state or "<MISSING>"
                zip_postal = paddress.postcode or "<MISSING>"
                locator_domain = DOMAIN
                page_url = base_url
                page_url = page_url if page_url else MISSING
                try:
                    location_name = location_names[idx1]
                except:
                    location_name = MISSING
                logger.info(f"Location Name: {idx1}: {location_name}")

                country_code = r.url.split("/")[-1]
                if country_code == "china":
                    country_code = "CH"
                if country_code == "france":
                    country_code = "FR"
                if country_code == "korea":
                    country_code = "KR"
                if country_code == "russia":
                    country_code = "RU"
                if country_code == "sweden":
                    country_code = "SE"
                if country_code == "united-arab-emirates":
                    country_code = "AE"
                if country_code == "united-kingdom":
                    country_code = "UK"
                if country_code == "united-states":
                    country_code = "US"
                if country_code == "store-germany":
                    country_code = "DE"

                store_number = "<MISSING>"
                phone = ""
                phone_data_to_be_parsed = telephone_data[-1]
                for match in phonenumbers.PhoneNumberMatcher(
                    phone_data_to_be_parsed, country_code
                ):
                    phone = phonenumbers.format_number(
                        match.number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
                    )
                phone = phone if phone else MISSING

                # Location Type
                location_type = "<MISSING>"
                if country_code == "US":
                    if "@" in latlng_from_googlemap_url_deduped[idx1]:
                        latitude = (
                            latlng_from_googlemap_url_deduped[idx1]
                            .split("@")[1]
                            .split(",")[0]
                            or "<MISSING>"
                        )
                        longitude = (
                            latlng_from_googlemap_url_deduped[idx1]
                            .split("@")[1]
                            .split(",")[1]
                            or "<MISSING>"
                        )
                    else:
                        latitude = "<MISSING>"
                        longitude = "<MISSING>"
                else:
                    try:
                        latitude = (
                            latlng_from_googlemap_url_deduped[idx1]
                            .split("@")[1]
                            .split(",")[0]
                        )
                        longitude = (
                            latlng_from_googlemap_url_deduped[idx1]
                            .split("@")[1]
                            .split(",")[1]
                        )
                    except:
                        latitude = MISSING
                        longitude = MISSING

                hours_of_operation = MISSING
                raw_address = address_raw
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


def fetch_data_uae():
    session = SgRequests()
    for urlnum, base_url in enumerate(urls_for_all_countries[0:]):
        if "united-arab-emirates" in base_url:
            r = session.get(base_url, headers=headers)
            tree = html.fromstring(r.text, "lxml")
            tds = tree.xpath(
                '//div[@class="column main"]//div[@data-content-type="html"]'
            )

            for idx, td in enumerate(tds):
                address_data2_temp = []
                # Location Names
                location_names = td.xpath("./h3/descendant::text()")

                # Address Data
                address_data = td.xpath("./text()")
                address_data1 = [" ".join(i.split()) for i in address_data]
                address_data2 = [i for i in address_data1 if i]
                address_data2 = ", ".join(address_data2)
                address_data2_temp.append(address_data2)

                logger.info(f"Addresses Found: {address_data2_temp}")

                telephone_data = td.xpath("./span/text()")
                logger.info(f"Phone Numbers: {idx}: \n{telephone_data}")

                # Latitude and longitude data
                latlng_from_googlemap_url = td.xpath(
                    '//a[contains(text(), "Map")]/@href'
                )
                logger.info(f"latlng data: {latlng_from_googlemap_url}")
                latlng_from_googlemap_url_deduped = list(
                    dict.fromkeys(latlng_from_googlemap_url)
                )

            for idx1, address in enumerate(address_data2_temp):
                address_raw = "".join(address)
                if "Russia" not in address_raw.lower():
                    address_raw = address_raw + ", " + "Russia"
                else:
                    address_raw = address_raw

                logger.info(f"Parsing the address: {idx1}: {address_raw}")
                paddress = parse_address_intl(address_raw)
                logger.info(f"Parsed Address: {paddress}")

                street_address = paddress.street_address_1 or "<MISSING>"
                street_address = street_address.replace("Byredo Dubai ", "")
                logger.info(f"Street Address: {street_address}")

                city = paddress.city or "<MISSING>"
                state = paddress.state or "<MISSING>"
                zip_postal = paddress.postcode or "<MISSING>"
                locator_domain = DOMAIN
                page_url = base_url
                page_url = page_url if page_url else MISSING
                try:
                    location_name = location_names[idx1]
                except:
                    location_name = MISSING
                logger.info(f"Location Name: {idx1}: {location_name}")

                country_code = r.url.split("/")[-1]
                if country_code == "china":
                    country_code = "CH"
                if country_code == "france":
                    country_code = "FR"
                if country_code == "korea":
                    country_code = "KR"
                if country_code == "russia":
                    country_code = "RU"
                if country_code == "sweden":
                    country_code = "SE"
                if country_code == "united-arab-emirates":
                    country_code = "AE"
                if country_code == "united-kingdom":
                    country_code = "UK"
                if country_code == "united-states":
                    country_code = "US"
                if country_code == "store-germany":
                    country_code = "DE"

                store_number = "<MISSING>"
                phone = ""
                try:
                    phone_data_to_be_parsed = telephone_data[-1]
                    for match in phonenumbers.PhoneNumberMatcher(
                        phone_data_to_be_parsed, country_code
                    ):
                        phone = phonenumbers.format_number(
                            match.number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
                        )
                    phone = phone if phone else MISSING
                except:
                    phone = MISSING

                # Location Type
                location_type = "<MISSING>"
                if country_code == "US":
                    if "@" in latlng_from_googlemap_url_deduped[idx1]:
                        latitude = (
                            latlng_from_googlemap_url_deduped[idx1]
                            .split("@")[1]
                            .split(",")[0]
                            or "<MISSING>"
                        )
                        longitude = (
                            latlng_from_googlemap_url_deduped[idx1]
                            .split("@")[1]
                            .split(",")[1]
                            or "<MISSING>"
                        )
                    else:
                        latitude = "<MISSING>"
                        longitude = "<MISSING>"
                else:
                    try:
                        latitude = (
                            latlng_from_googlemap_url_deduped[idx1]
                            .split("@")[1]
                            .split(",")[0]
                        )
                        longitude = (
                            latlng_from_googlemap_url_deduped[idx1]
                            .split("@")[1]
                            .split(",")[1]
                        )
                    except:
                        latitude = MISSING
                        longitude = MISSING

                hours_of_operation = MISSING
                raw_address = address_raw
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


def fetch_data_korea():
    session = SgRequests()
    for urlnum, base_url in enumerate(urls_for_all_countries[0:]):
        if "korea" in base_url:
            r = session.get(base_url, headers=headers)
            tree = html.fromstring(r.text, "lxml")
            tds = tree.xpath('//div[@class="column main"]//table/tbody')
            for idxuk, td in enumerate(tds):
                location_names = td.xpath("//tr/td/h3//descendant::text()")
                address_data = td.xpath(
                    "//tr/td//text()[count(preceding-sibling::h2)=$count]",
                    count="{}".format(idxuk),
                )
                address_data1 = " ".join(address_data)
                logger.info(f"Address Data: {address_data1}")
                address_data2 = address_data1.split("Map")
                address_data3 = [" ".join(i.split()) for i in address_data2 if i]
                address_data3 = [i for i in address_data3 if i]
                logger.info(f"Number of Addresses Found: {address_data3}")
                phone_numbers = ["+" + i.split("+")[-1] for i in address_data3 if i]
                logger.info(f"Phone Numbers: {idxuk}: \n{phone_numbers}")
                latlng_from_googlemap_url = td.xpath(
                    '//a[contains(text(), "Map")]/@href'
                )
                logger.info(f"latlng data: {latlng_from_googlemap_url}")
                latlng_from_googlemap_url_deduped = list(
                    dict.fromkeys(latlng_from_googlemap_url)
                )

            for idxuk1, address in enumerate(address_data3):
                logger.info(f"Parsing the address: {idxuk1}: {address}")
                address_without_phone_data = address.split("+")
                address_wpd = address_without_phone_data[0].strip()
                logger.info(f"Address without Phone data: {idxuk1}: {address_wpd}")

                address_wpd1 = address_wpd.split("Temporarily closed")[0].strip()
                paddress = parse_address_intl(address_wpd1)
                logger.info(f"Parsed Address: {paddress}")

                street_address = paddress.street_address_1 or "<MISSING>"
                logger.info(f"Street Address: {street_address}")

                city = paddress.city or "<MISSING>"
                state = paddress.state or "<MISSING>"
                zip_postal = paddress.postcode or "<MISSING>"
                locator_domain = DOMAIN
                page_url = base_url
                page_url = page_url if page_url else MISSING

                try:
                    location_name = location_names[idxuk1]
                except:
                    location_name = MISSING
                logger.info(f"Location Name: {idxuk1}: {location_name}")

                country_code = r.url.split("/")[-1]
                if country_code == "china":
                    country_code = "CH"
                if country_code == "france":
                    country_code = "FR"
                if country_code == "korea":
                    country_code = "KR"
                if country_code == "russia":
                    country_code = "RU"
                if country_code == "sweden":
                    country_code = "SE"
                if country_code == "united-arab-emirates":
                    country_code = "AE"
                if country_code == "united-kingdom":
                    country_code = "UK"
                if country_code == "united-states":
                    country_code = "US"
                if country_code == "store-germany":
                    country_code = "DE"

                store_number = "<MISSING>"
                phone = ""
                phone_data_to_be_parsed = phone_numbers[idxuk1]
                for match in phonenumbers.PhoneNumberMatcher(
                    phone_data_to_be_parsed, country_code
                ):
                    phone = phonenumbers.format_number(
                        match.number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
                    )
                phone = phone if phone else MISSING
                location_type = "<MISSING>"
                if country_code == "US":
                    if "@" in latlng_from_googlemap_url_deduped[idxuk1]:
                        latitude = (
                            latlng_from_googlemap_url_deduped[idxuk1]
                            .split("@")[1]
                            .split(",")[0]
                            or "<MISSING>"
                        )
                        longitude = (
                            latlng_from_googlemap_url_deduped[idxuk1]
                            .split("@")[1]
                            .split(",")[1]
                            or "<MISSING>"
                        )
                    else:
                        latitude = "<MISSING>"
                        longitude = "<MISSING>"
                else:
                    latitude = (
                        latlng_from_googlemap_url_deduped[idxuk1]
                        .split("@")[1]
                        .split(",")[0]
                        or "<MISSING>"
                    )
                    longitude = (
                        latlng_from_googlemap_url_deduped[idxuk1]
                        .split("@")[1]
                        .split(",")[1]
                        or "<MISSING>"
                    )
                hours_of_operation = MISSING
                logger.info(f"hours of operation raw: {hours_of_operation}")
                raw_address = address_wpd
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
        global_data = list(fetch_data_global())
        russia_data = list(fetch_data_russia())
        global_data.extend(russia_data)
        uae_data = list(fetch_data_uae())
        global_data.extend(uae_data)
        korea_data = list(fetch_data_korea())
        global_data.extend(korea_data)
        for rec in global_data:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
