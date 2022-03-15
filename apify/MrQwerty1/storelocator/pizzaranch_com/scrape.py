import json
from sglogging import sglog
from concurrent import futures
from lxml import html
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

log = sglog.SgLogSetup().get_logger(logger_name="pizzaranch.com")


def get_hours(url):
    _tmp = []
    session = SgRequests()
    r = session.get(url)
    tree = html.fromstring(r.text)

    hours = tree.xpath("//div[@id='c-hours-collapse']//table/tbody/tr")
    for h in hours:
        day = "".join(h.xpath("./td[@class='c-location-hours-details-row-day']/text()"))
        time = " ".join(
            h.xpath(
                ".//span[@class='c-location-hours-details-row-intervals-instance js-location-hours-interval-instance']//text()"
            )
        )
        if time:
            _tmp.append(f"{day} {time}")
        else:
            _tmp.append(f"{day} Closed")

    hours_of_operation = ";".join(_tmp).replace("day", "day:") or "<MISSING>"

    return hours_of_operation


def fetch_data():
    locator_domain = "https://pizzaranch.com"
    session = SgRequests()

    search_url = "https://pizzaranch.com/all-locations/search-results/p1?state=*"
    while True:
        urls = set()
        hours = dict()
        r = session.get(search_url)
        tree = html.fromstring(r.text)
        size = tree.xpath("//location-info-panel")
        text = "".join(
            tree.xpath("//script[contains(text(), 'var locations = ')]/text()")
        )
        text = text.split("var locations = ")[1].replace(";", "")
        js = json.loads(text)

        for j in js:
            url = j.get("website")
            if url:
                urls.add(url)

        with futures.ThreadPoolExecutor(max_workers=12) as executor:
            future_to_url = {executor.submit(get_hours, url): url for url in urls}
            for future in futures.as_completed(future_to_url):
                k = future_to_url[future].split("/")[-1]
                hours[k] = future.result()

        for j in js:
            location_name = j.get("title")
            street_address = j.get("address1")
            city = j.get("city")
            state = j.get("state")
            postal = j.get("zipCode")
            country_code = "US"
            store_number = j.get("id")
            phone = j.get("phone")
            location_type = "<MISSING>"
            latitude = j.get("lat")
            longitude = j.get("lng")
            page_url = j.get("website") or "<MISSING>"

            hours_of_operation = "<MISSING>"
            try:
                key = page_url.split("/")[-1]
                hours_of_operation = hours[key]
            except:
                hours_of_operation = "<MISSING>"

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

        if len(size) < 12:
            break

        next_page = "".join(tree.xpath('//li[@class="next"]/a/@href')).strip()
        if len(next_page) > 0:
            search_url = next_page
        else:
            break


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
