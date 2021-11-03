from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
import phonenumbers
from lxml import html
import ssl
import re

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
MISSING = SgRecord.MISSING

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
            "france" in base_url
            or "sweden" in base_url
            or "united-kingdom" in base_url
            or "united-states" in base_url
            or "store-germany" in base_url
        ):
            r = session.get(base_url, headers=headers)
            tree = html.fromstring(r.text, "lxml")
            tds = tree.xpath('//div[@class="column main"]//table/tbody')
            for idxuk, td in enumerate(tds):

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

            for idx1, address in enumerate(address_data3):
                logger.info(f"[{idx1}] Parsing the address: {address}")
                address_without_phone_data = address.split("+")
                address_wpd = address_without_phone_data[0].strip()
                logger.info(
                    f"[{idx1}] Address without Phone data: {idx1}: {address_wpd}"
                )

                address_wpd1 = address_wpd.split("Temporarily closed")[0].strip()
                paddress = parse_address_intl(address_wpd1)
                logger.info(f"[{idx1}] Parsed Address: {paddress}")

                street_address = paddress.street_address_1 or MISSING
                logger.info(f"[{idx1}] Street Address: {street_address}")

                city = paddress.city or MISSING
                state = paddress.state or MISSING
                zip_postal = paddress.postcode or MISSING
                locator_domain = DOMAIN
                page_url = base_url
                page_url = page_url if page_url else MISSING

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

                store_number = MISSING
                phone = ""

                phone_data_to_be_parsed = phone_numbers[idx1]
                for match in phonenumbers.PhoneNumberMatcher(
                    phone_data_to_be_parsed, country_code
                ):
                    phone = phonenumbers.format_number(
                        match.number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
                    )
                phone = phone if phone else MISSING
                location_type = MISSING
                latitude = ""
                longitude = ""
                try:
                    if country_code == "US":
                        if "@" in latlng_from_googlemap_url_deduped[idx1]:
                            latitude = (
                                latlng_from_googlemap_url_deduped[idx1]
                                .split("@")[1]
                                .split(",")[0]
                                or MISSING
                            )
                            longitude = (
                                latlng_from_googlemap_url_deduped[idx1]
                                .split("@")[1]
                                .split(",")[1]
                                or MISSING
                            )
                        else:
                            latitude = MISSING
                            longitude = MISSING
                    else:
                        latitude = (
                            latlng_from_googlemap_url_deduped[idx1]
                            .split("@")[1]
                            .split(",")[0]
                            or MISSING
                        )
                        longitude = (
                            latlng_from_googlemap_url_deduped[idx1]
                            .split("@")[1]
                            .split(",")[1]
                            or MISSING
                        )
                except:
                    latitude = MISSING
                    longitude = MISSING
                hours_of_operation = MISSING
                logger.info(f"hours of operation raw: {hours_of_operation}")
                raw_address = address_wpd

                location_name = get_location_name(raw_address, country_code)
                logger.info(f"Location Name: {idx1}: {location_name}")

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


def fetch_data_china():
    session = SgRequests()

    for urlnum, base_url in enumerate(urls_for_all_countries[0:]):
        if "china" in base_url:
            r = session.get(base_url, headers=headers)
            tree = html.fromstring(r.text, "lxml")
            tds = tree.xpath('//div[@class="column main"]//table/tbody')
            for idxuk, td in enumerate(tds):

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
                address_data4 = [
                    " ".join(i.split("China")[-1].split()).lstrip(",").strip()
                    for i in address_data3
                ]
                phone_numbers = []
                for i in address_data4:
                    if "+" in i:
                        phone_numbers.append(i)
                    else:
                        j = i.split(" ")[-1]
                        phone_numbers.append(j)
                logger.info(f"Phone Numbers: {idxuk}: \n{phone_numbers}")
                latlng_from_googlemap_url = td.xpath(
                    '//a[contains(text(), "Map")]/@href'
                )
                logger.info(f"latlng data: {latlng_from_googlemap_url}")
                latlng_from_googlemap_url_deduped = list(
                    dict.fromkeys(latlng_from_googlemap_url)
                )

            for idx1, address in enumerate(address_data3):
                logger.info(f"Parsing the address: {idx1}: {address}")
                address_without_phone_data = address.replace(
                    phone_numbers[idx1], ""
                ).strip()

                address_wpd = address_without_phone_data.strip()
                logger.info(f"Address without Phone data: {idx1}: {address_wpd}")

                address_wpd1 = address_wpd.split("Temporarily closed")[0].strip()
                paddress = parse_address_intl(address_wpd1)
                logger.info(f"Parsed Address: {paddress}")

                street_address = paddress.street_address_1 or MISSING
                logger.info(f"Street Address: {street_address}")

                city = paddress.city or MISSING
                state = paddress.state or MISSING
                zip_postal = paddress.postcode or MISSING
                locator_domain = DOMAIN
                page_url = base_url
                page_url = page_url if page_url else MISSING

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

                store_number = MISSING

                phone = phone_numbers[idx1]
                phone = phone if phone else MISSING
                location_type = MISSING
                if country_code == "US":
                    if "@" in latlng_from_googlemap_url_deduped[idx1]:
                        latitude = (
                            latlng_from_googlemap_url_deduped[idx1]
                            .split("@")[1]
                            .split(",")[0]
                            or MISSING
                        )
                        longitude = (
                            latlng_from_googlemap_url_deduped[idx1]
                            .split("@")[1]
                            .split(",")[1]
                            or MISSING
                        )
                    else:
                        latitude = MISSING
                        longitude = MISSING
                else:
                    latitude = (
                        latlng_from_googlemap_url_deduped[idx1]
                        .split("@")[1]
                        .split(",")[0]
                        or MISSING
                    )
                    longitude = (
                        latlng_from_googlemap_url_deduped[idx1]
                        .split("@")[1]
                        .split(",")[1]
                        or MISSING
                    )
                hours_of_operation = MISSING
                logger.info(f"hours of operation raw: {hours_of_operation}")
                raw_address = address_wpd
                location_name = get_location_name(raw_address, country_code)
                logger.info(f"Location Name: {idx1}: {location_name}")

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

                street_address = paddress.street_address_1 or MISSING
                logger.info(f"Street Address: {street_address}")

                city = paddress.city or MISSING
                state = paddress.state or MISSING
                zip_postal = paddress.postcode or MISSING
                locator_domain = DOMAIN
                page_url = base_url
                page_url = page_url if page_url else MISSING

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

                store_number = MISSING
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
                location_type = MISSING
                if country_code == "US":
                    if "@" in latlng_from_googlemap_url_deduped[idx1]:
                        latitude = (
                            latlng_from_googlemap_url_deduped[idx1]
                            .split("@")[1]
                            .split(",")[0]
                            or MISSING
                        )
                        longitude = (
                            latlng_from_googlemap_url_deduped[idx1]
                            .split("@")[1]
                            .split(",")[1]
                            or MISSING
                        )
                    else:
                        latitude = MISSING
                        longitude = MISSING
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

                location_name = get_location_name(raw_address, country_code)
                logger.info(f"Location Name: {idx1}: {location_name}")

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

                street_address = paddress.street_address_1 or MISSING
                street_address = street_address.replace("Byredo Dubai ", "")
                logger.info(f"Street Address: {street_address}")

                city = paddress.city or MISSING
                state = paddress.state or MISSING
                zip_postal = paddress.postcode or MISSING
                locator_domain = DOMAIN
                page_url = base_url
                page_url = page_url if page_url else MISSING

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

                store_number = MISSING
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
                location_type = MISSING
                if country_code == "US":
                    if "@" in latlng_from_googlemap_url_deduped[idx1]:
                        latitude = (
                            latlng_from_googlemap_url_deduped[idx1]
                            .split("@")[1]
                            .split(",")[0]
                            or MISSING
                        )
                        longitude = (
                            latlng_from_googlemap_url_deduped[idx1]
                            .split("@")[1]
                            .split(",")[1]
                            or MISSING
                        )
                    else:
                        latitude = MISSING
                        longitude = MISSING
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

                location_name = get_location_name(raw_address, country_code)
                logger.info(f"Location Name: {idx1}: {location_name}")

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

            for idx1, address in enumerate(address_data3):
                logger.info(f"Parsing the address: {idx1}: {address}")
                address_without_phone_data = address.split("+")
                address_wpd = address_without_phone_data[0].strip()
                logger.info(f"Address without Phone data: {idx1}: {address_wpd}")

                address_wpd1 = address_wpd.split("Temporarily closed")[0].strip()
                paddress = parse_address_intl(address_wpd1)
                logger.info(f"Parsed Address: {paddress}")

                street_address = paddress.street_address_1 or MISSING
                logger.info(f"Street Address: {street_address}")

                city = paddress.city or MISSING
                state = paddress.state or MISSING
                zip_postal = paddress.postcode or MISSING
                locator_domain = DOMAIN
                page_url = base_url
                page_url = page_url if page_url else MISSING

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

                store_number = MISSING
                phone = ""
                phone_data_to_be_parsed = phone_numbers[idx1]
                for match in phonenumbers.PhoneNumberMatcher(
                    phone_data_to_be_parsed, country_code
                ):
                    phone = phonenumbers.format_number(
                        match.number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
                    )
                phone = phone if phone else MISSING
                location_type = MISSING
                if country_code == "US":
                    if "@" in latlng_from_googlemap_url_deduped[idx1]:
                        latitude = (
                            latlng_from_googlemap_url_deduped[idx1]
                            .split("@")[1]
                            .split(",")[0]
                            or MISSING
                        )
                        longitude = (
                            latlng_from_googlemap_url_deduped[idx1]
                            .split("@")[1]
                            .split(",")[1]
                            or MISSING
                        )
                    else:
                        latitude = MISSING
                        longitude = MISSING
                else:
                    latitude = (
                        latlng_from_googlemap_url_deduped[idx1]
                        .split("@")[1]
                        .split(",")[0]
                        or MISSING
                    )
                    longitude = (
                        latlng_from_googlemap_url_deduped[idx1]
                        .split("@")[1]
                        .split(",")[1]
                        or MISSING
                    )
                hours_of_operation = MISSING
                logger.info(f"hours of operation raw: {hours_of_operation}")
                raw_address = address_wpd

                location_name = get_location_name(raw_address, country_code)
                logger.info(f"Location Name: {idx1}: {location_name}")

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


def get_location_name(r_address, country_code):
    location_name = MISSING
    r_address_split = re.split(r"\d", r_address)[0]
    locname = r_address_split.split("Makeup available")[-1]
    locname = locname.strip()

    # Location Name Rules for France ( FR )
    if "FR" in country_code:
        if "Lyon Printemps Lyon" in locname:
            location_name = "Printemps Lyon"

        elif "Lille Printemps Lille" in locname:
            location_name = "Printemps Lille"
        else:
            location_name = locname

    # Rules for Sweden ( SE)
    if "SE" in country_code:
        if "Byredo Stockholm Mäster Samuelsgatan" in locname:
            location_name = "Byredo Stockholm"
        elif "Åhlens Klarabergsgatan" in locname:
            location_name = "Åhlens"
        elif "Stockholm Nitty Gritty Krukmakargatan" in locname:
            location_name = "Nitty Gritty"
        elif "NK Hamngatan" in locname:
            location_name = "NK"
        elif "NK Östra Hamngatan" in locname:
            location_name = "NK"
        else:
            location_name = locname

    # Rules for London ( UK )
    if "UK" in country_code:
        if "London Liberty Regent Street W" in locname:
            location_name = "Liberty"
        elif "London Harrods" in locname:
            location_name = "Harrods"
        elif "Space NK" in locname:
            location_name = "Space NK"
        elif "Selfridges" in locname:
            location_name = "Selfridges"
        else:
            location_name = locname

    # Rules for USA ( US )
    if "US" in country_code:
        if "Los Angeles Nordstrom Century City" in locname:
            location_name = "Nordstrom Century City"

        elif "Atlanta Neiman Marcus" in locname:
            location_name = "Neiman Marcus"

        elif "New York Nordstorm NYC" in locname:
            location_name = "Nordstorm NYC"

        elif "Dallas Neiman Marcus NorthPark" in locname:
            location_name = "Neiman Marcus NorthPark"

        elif "Los Angeles Nordstrom The Grove" in locname:
            location_name = "Nordstrom The Grove"

        elif "New York Bergdorf Goodman" in locname:
            location_name = "Bergdorf Goodman"

        elif "Miami Neiman Marcus Merrick Park" in locname:
            location_name = "Neiman Marcus Merrick Park"

        elif "Los Angeles Neiman Marcus" in locname:
            location_name = "Neiman Marcus"

        elif "New York Bloomingdale" in locname:
            location_name = "Bloomingdale's"
        else:
            location_name = locname

    # Rules for Germany ( DE )
    if "DE" in country_code:
        if "Berlin Galeries Lafayette Friedrichstr" in locname:
            location_name = "Galeries Lafayette"

        elif "Berlin KaDeWe Tauentzienstraße" in locname:
            location_name = "KaDeWe"

        elif "Düsseldorf Breuninger Düsseldorf" in locname:
            location_name = "Breuninger Düsseldorf"

        elif "Munich Ludwig Beck" in locname:
            location_name = "Ludwig Beck"

        elif "Munich Oberpollinger" in locname:
            location_name = "Oberpollinger"

        elif "Hamburg Alsterhaus" in locname:
            location_name = "Alsterhaus"
        else:
            location_name = locname

    # Rules for China ( CH )
    if "CH" in country_code:
        if "Shanghai Byredo Plaza" in locname:
            location_name = "Byredo Plaza"

        elif "Nanjing Byredo DEJI" in locname:
            location_name = "Byredo DEJI"

        elif "Beijing TaiKoo Li Sanlitun" in locname:
            location_name = "TaiKoo Li Sanlitun"

        elif "Hong Kong Lane Crawford" in locname:
            location_name = "Lane Crawford"

        elif "Byredo K" in locname:
            location_name = "Byredo K11 Musea"

        elif "Shanghai IFC Store C" in locname:
            location_name = "IFC"

        elif "Beijing Byredo SKP South Store D" in locname:
            location_name = "Byredo SKP South"

        elif "Hangzhou Byredo in" in locname:
            location_name = "Byredo in77"

        elif "Lane Crawford" in locname:
            location_name = "Lane Crawford"

        elif "Shenzhen MIXCW Store" in locname:
            location_name = "MIXCW"
        else:
            location_name = locname

    # Rules For Russia ( RU)
    if "RU" in country_code:
        if "Byredo Moscow, Malaya Bronnaya St." in locname:
            location_name = "Byredo Moscow"
        else:
            location_name = locname

    # Rules for United Arab Emirates ( AE )
    if "AE" in country_code:
        if "Byredo Dubai, The Dubai Mall," in locname:
            location_name = "Byredo Dubai"
        else:
            location_name = locname

    # Rules for Korea ( KR )
    if "KR" in country_code:
        location_name = locname

    return location_name


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.RAW_ADDRESS,
                }
            )
        )
    ) as writer:
        global_data = list(fetch_data_global())

        china_data = list(fetch_data_china())
        global_data.extend(china_data)

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
