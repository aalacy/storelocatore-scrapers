import yaml
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from lxml import html
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


log = sglog.SgLogSetup().get_logger(logger_name="mypiada.com")


def fetch_data():
    locator_domain = "https://mypiada.com/"
    page_url = "https://mypiada.com/locations?l=all"
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(),'var stores = [],')]/text()"))
    text = text.split("var marker;")[1:]

    for t in text:
        j = yaml.load(
            t.split("stores.push(")[1].split(");")[0].replace("\t", ""),
            Loader=yaml.Loader,
        )

        a = j.get("address")
        root = html.fromstring(a)
        line = root.xpath("//text()")
        line = list(filter(None, [l.strip() for l in line]))

        street_address = line[0]
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"

        store_number = j.get("oloID")
        location_name = j.get("name")
        ph = j.get("phone")
        location_type = SgRecord.MISSING
        if "Coming Soon" in ph:
            phone = SgRecord.MISSING
            location_type = "Coming Soon"
        else:
            phone = ph.split(">")[-1].replace("Â", "").strip() or "<MISSING>"
        loc = j.get("geo") or "<MISSING>,<MISSING>"
        latitude, longitude = loc.split(",")

        isclosed = j.get("temporarilyClosed")
        if isclosed:
            hours_of_operation = "Closed"
        else:
            hours_of_operation = f"{j.get('openTime')} - {j.get('closeTime')}"

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
