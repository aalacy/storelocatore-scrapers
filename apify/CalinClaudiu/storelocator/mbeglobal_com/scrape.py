from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup as b4
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape import sgpostal as parser

import re

logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
import json


def clean(x):
    if not x or x.lower() in ["none", "na"]:
        return SgRecord.MISSING
    else:
        return x


def fix_comma(x):
    x = x.replace("None", "")
    h = []
    try:
        for i in x.split(","):
            if len(i.strip()) >= 1:
                h.append(i)
        return ", ".join(h)
    except Exception:
        return x


def ret_record(record):
    MISSING = SgRecord.MISSING
    page_url = SgRecord.MISSING
    location_name = SgRecord.MISSING
    street_address = SgRecord.MISSING
    city = SgRecord.MISSING
    state = SgRecord.MISSING
    zip_postal = SgRecord.MISSING
    country_code = SgRecord.MISSING
    store_number = SgRecord.MISSING
    phone = SgRecord.MISSING
    location_type = SgRecord.MISSING
    latitude = SgRecord.MISSING
    longitude = SgRecord.MISSING
    hours_of_operation = SgRecord.MISSING
    raw_address = SgRecord.MISSING

    try:
        data1 = list(b4(record["Name"], "lxml").stripped_strings)
    except Exception:
        pass
    try:
        location_name = " - ".join(data1)
    except Exception:
        pass
    try:
        data2 = list(b4(record["InfoWindowMarkup"], "lxml").stripped_strings)
    except Exception:
        pass

    try:
        street_address = str(data2[2]).strip()
        street_address = re.sub("[\t\r\n ]+", " ", street_address)
    except Exception:
        pass

    try:
        raw_address = str(data2[2]).replace("Contact", "").strip()
    except Exception:
        pass

    try:
        city = data2[3]
    except Exception:
        pass

    try:
        store_number = str(record["ID"])
    except Exception:
        pass

    try:
        phone = str(data2[-2]).replace("Tel.", "")
        try:
            phone = phone.split("+", 1)[1]
            phone = "+" + phone
        except Exception:
            pass
    except Exception:
        pass

    try:
        location_type = data2[0]
    except Exception:
        pass

    try:
        latitude = str(record["Coords"]["Lat"])
    except Exception:
        pass

    try:
        longitude = str(record["Coords"]["Lng"])
    except Exception:
        pass

    parsed = parser.parse_address_intl(raw_address)
    country_code = parsed.country if parsed.country else MISSING
    street_address = parsed.street_address_1 if parsed.street_address_1 else MISSING
    street_address = (
        (street_address + ", " + parsed.street_address_2)
        if parsed.street_address_2
        else street_address
    )
    city = parsed.city if parsed.city else MISSING
    state = parsed.state if parsed.state else MISSING
    zip_postal = parsed.postcode if parsed.postcode else MISSING

    return SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=clean(zip_postal),
        country_code=country_code,
        store_number=store_number,
        phone=clean(phone),
        location_type=location_type,
        latitude=latitude,
        longitude=longitude,
        locator_domain="https://www.starbucks.com/",
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )


def crawl(session):
    url = "https://www.mbeglobal.com/WS/wsStores.asmx/FindNearGlobal"
    headers = {}
    headers["Accept"] = "application/json, text/javascript, */*; q=0.01"
    headers["Accept-Encoding"] = "gzip, deflate, br"
    headers["Accept-Language"] = "en-US,en;q=0.9,ro;q=0.8,es;q=0.7"
    headers["Connection"] = "keep-alive"
    headers["Content-Length"] = "76"
    headers["Content-Type"] = "application/json"
    headers["Host"] = "www.mbeglobal.com"
    headers["Origin"] = "https://www.mbeglobal.com"
    headers["Referer"] = "https://www.mbeglobal.com/store-locator"
    headers["Sec-Fetch-Dest"] = "empty"
    headers["Sec-Fetch-Mode"] = "cors"
    headers["Sec-Fetch-Site"] = "same-origin"
    headers[
        "User-Agent"
    ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
    headers["X-Requested-With"] = "XMLHttpRequest"
    headers[
        "sec-ch-ua"
    ] = '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"'
    headers["sec-ch-ua-mobile"] = "?0"
    headers["sec-ch-ua-platform"] = '"Windows"'

    data = (
        '{"coords":{"lat":52.3675734,"lng":4.9041389},"radius":99962.147977050741616}'
    )

    resp = SgRequests.raise_on_err(session.post(url, headers=headers, data=data)).json()
    resp = json.loads(resp["d"]["Props"]["DataForMap"])
    for rec in resp:
        yield rec

    data = (
        '{"coords":{"lat":27.797456,"lng":-97.409170},"radius":99962.147977050741616}'
    )
    headers["Content-Length"] = "76"
    resp = SgRequests.raise_on_err(session.post(url, headers=headers, data=data)).json()
    resp = json.loads(resp["d"]["Props"]["DataForMap"])
    for rec in resp:
        yield rec


if __name__ == "__main__":
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.PHONE,
                },
                fail_on_empty_id=True,
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        with SgRequests() as http:
            for rec in crawl(http):
                writer.write_row(ret_record(rec))
