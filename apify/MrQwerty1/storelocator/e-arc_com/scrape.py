import json
from concurrent import futures
from lxml import html
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "e-arc.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()


def get_hours(url):
    _id = url.split("/")[-2]
    log.info(url)
    r = session.get(url)
    tree = html.fromstring(r.text)
    hours = (
        ";".join(tree.xpath("//p[./span[contains(text(),'Hours:')]]/text()")).strip()
        or "<MISSING>"
    )

    if hours.find("(") != -1:
        hours = hours.replace("(Production)", "").split("(")[0].strip()

    if hours.find("Production") != -1:
        hours = hours.split(";Production")[0].replace("Walk-in", "").strip()
    elif hours.find("RIOT") != -1:
        hours = hours.split(";RIOT")[0].replace("ARC Repro is open", "").strip()

    return {_id: hours}


def fetch_data():
    urls = []
    hours = []
    locator_domain = "https://www.e-arc.com"
    r = session.get("https://www.e-arc.com/location/")
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'var servicecenters')]/text()")
    )
    text = (
        text.split("var servicecenters = ")[1]
        .split("var $result")[0]
        .replace("];", "")
        .strip()[:-1]
        + "]"
    )
    js = json.loads(text)

    for j in js:
        j = j.get("servicecenter")
        country = j.get("country_name")
        if country == "Canada" or country == "United States":
            urls.append(j.get("permalink"))

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_hours, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            hours.append(future.result())

    hours = {k: v for elem in hours for (k, v) in elem.items()}

    for j in js:
        j = j.get("servicecenter")
        page_url = j.get("permalink") or "<MISSING>"
        _id = page_url.split("/")[-2]
        location_name = j.get("title")
        street_address = j.get("street_address") or "<MISSING>"
        if street_address.find("<br>") != -1:
            street_address = street_address.split("<br>")[-1]
        elif street_address.find("(") != -1:
            street_address = street_address.split("(")[0].strip()
        city = j.get("city") or "<MISSING>"
        state = j.get("province") or "<MISSING>"
        if city == state:
            state = j.get("regions")

        postal = j.get("postalcodes") or "<MISSING>"
        country = j.get("country_name") or "<MISSING>"
        if country == "United States":
            country_code = "US"
        elif country == "Canada":
            country_code = "CA"
        else:
            continue
        store_number = "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        if phone.find("/") != -1:
            phone = phone.replace("(Production)", "").split("/")[0].strip()
        elif phone.find(" or ") != -1:
            phone = phone.split(" or ")[0].strip()
        elif phone.find(" - ") != -1:
            phone = phone.split(" - ")[0].strip()

        latitude = j.get("location_latitude") or "<MISSING>"
        longitude = j.get("location_longitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = hours.get(_id)
        if hours_of_operation[-1] == ";":
            hours_of_operation = "".join(hours_of_operation[:-1]).strip()

        yield SgRecord(
            locator_domain=locator_domain,
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
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
