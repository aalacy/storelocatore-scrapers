from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape import sgpostal as parser


logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")


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
        location_name = record["name"]
    except Exception as e:
        logzilla.error("location_name\n", exc_info=e)
        pass

    try:
        store_number = str(record["id"])
    except Exception as e:
        logzilla.error("store_number\n", exc_info=e)
        pass

    try:
        phone = str(record["phone"])
    except Exception as e:
        logzilla.error("phone\n", exc_info=e)
        pass

    try:
        location_type = str(record["category"])
    except Exception as e:
        logzilla.error("location_type\n", exc_info=e)
        pass

    try:
        latitude = str(record["latitude"])
    except Exception as e:
        logzilla.error("latitude\n", exc_info=e)
        pass

    try:
        longitude = record["longitude"]
    except Exception as e:
        logzilla.error("longitude\n", exc_info=e)
        pass

    try:
        page_url = str(record["url"])
    except Exception as e:
        logzilla.error("page_url = \n", exc_info=e)
        pass
    try:
        raw_address = record["address"]
    except Exception as e:
        logzilla.error("raw_address\n", exc_info=e)
        pass
    parsed = parser.parse_address_usa(raw_address)
    street_address = parsed.street_address_1 if parsed.street_address_1 else MISSING
    street_address = (
        (street_address + ", " + parsed.street_address_2)
        if parsed.street_address_2
        else street_address
    )
    city = parsed.city if parsed.city else MISSING
    country_code = parsed.country if parsed.country else MISSING
    state = parsed.state if parsed.state else MISSING
    zip_postal = parsed.postcode if parsed.postcode else MISSING

    try:
        hours_of_operation = str(
            record["custom_field_1"].strip()
            + "; "
            + record["custom_field_2"].strip()
            + "; "
            + record["custom_field_3"].strip()
        )
    except Exception as e:
        logzilla.error("raw_address\n", exc_info=e)
        pass
    hours_of_operation = (
        str(hours_of_operation).replace("; ;", MISSING).replace(" ;", "")
    )
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
        locator_domain="www.shoepalace.com",
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )


def crawl(session):

    url = "https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/8158/stores.js"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }

    son = SgRequests.raise_on_err(session.get(url, headers=headers)).json()
    for i in son["stores"]:
        rec = ret_record(i)
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
                writer.write_row(rec)
