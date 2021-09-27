import json
from lxml import etree
from urllib.parse import urlencode

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}


def parse_ids(dom, session):
    ent_list = []
    ids = dom.xpath('//script[@id="paginator-ids-core"]/text()')
    urls = []
    if ids:
        ids = json.loads(ids[0])
        for e in ids:
            ent_list.append({"meta.id": {"$eq": e}})

        params = {
            "api_key": "f60a800cdb7af0904b988d834ffeb221",
            "v": "20160822",
            "filter": {"$or": ent_list},
            "languages": "en_GB",
            "limit": "50",
        }
        params = urlencode(params)
        url = "https://liveapi.yext.com/v2/accounts/1624327134898036854/entities?"

        urls = []
        data = session.get(url + params).json()
        for e in data["response"]["entities"]:
            urls.append(e["c_pageDestinationURL"])

    return urls


def fetch_all_locations(session):
    locations = []
    start_url = "https://all.accor.com/gb/world/hotels-accor-monde.shtml"
    traverse_directory(start_url, session, locations)

    return locations


def traverse_directory(url, session, locations):
    page = etree.HTML(session.get(url, headers=headers, timeout=180).text)
    sublocations = page.xpath('//*[@class="Teaser-link"]/@href')
    bookings = [url for url in sublocations if "index.en.shtml" in url]
    if len(bookings):
        for booking in bookings:
            if booking not in locations:
                locations.append(booking)
    else:
        for location in sublocations:
            traverse_directory(location, session, locations)


def fetch_data():
    domain = "accor.com"
    session = SgRequests(proxy_rotation_failure_threshold=3, retry_behavior=None)

    params = {
        "api_key": "f60a800cdb7af0904b988d834ffeb221",
        "v": "20160822",
        "filter": json.dumps({"websiteUrl.url": {"$contains": "all.accor"}}),
        "languages": "en_GB",
        "pageToken": None,
    }

    has_next = True

    while has_next:
        data = session.get(
            "https://liveapi.yext.com/v2/accounts/1624327134898036854/entities",
            params=params,
        ).json()

        entities = data["response"]["entities"]
        token = data["response"]["pageToken"]

        has_next = token is not None
        params["pageToken"] = token

        for location in entities:
            page_url = location["websiteUrl"]["url"]
            location_name = location["name"]
            location_type = location["meta"]["entityType"]
            store_number = location["meta"]["id"]

            address = location["address"]
            street_address = address["line1"]
            if address.get("line2"):
                street_address += f', {address["line2"]}'

            city = address["city"]
            postal = address.get("postalCode")
            country_code = address["countryCode"]

            geo = (
                location.get("geocodedCoordinate")
                or location.get("displayCoordinate")
                or location.get("yextDisplayCoordinate")
            )
            latitude = str(geo["latitude"])
            longitude = str(geo["longitude"])

            phone = location.get("mainPhone")

            location_hours = []
            if location.get("hours") is None:
                location_hours = None
            else:
                for day, intervals in location["hours"].items():
                    if day == "reopenDate" or day == "holidayHours":
                        continue

                    all_intervals = []
                    if intervals.get("isClosed") is not None:
                        location_hours.append(f"{day}: Closed")
                        break

                    for hour in intervals["openIntervals"]:
                        start = hour["start"]
                        end = hour["end"]
                        all_intervals.append(f"{start}-{end}")

                    hours = " ".join(all_intervals)
                    location_hours.append(f"{day}: {hours}")

            hours_of_operation = ", ".join(location_hours)

            yield SgRecord(
                locator_domain=domain,
                page_url=page_url,
                store_number=store_number,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=postal,
                country_code=country_code,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )


def write_output(data):
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for row in data:
            writer.write_row(row)


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
