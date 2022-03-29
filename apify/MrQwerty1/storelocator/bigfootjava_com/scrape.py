from concurrent import futures
from lxml import html
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter


def get_urls():
    r = session.get("https://bigfootjava.com/locations/", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='locationsList-item-link']/@href")


def get_data(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//span[@class='locationName']/text()")).strip()
    line = tree.xpath("//span[@class='locationAddress']/text()")
    line = list(filter(None, [l.strip() for l in line]))
    iscoming = "".join(line).lower()
    if iscoming.find("coming soon") != -1:
        return

    street_address = line[0]
    if street_address.endswith(","):
        street_address = street_address[:-1]
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = " ".join(line.split()[:-1])
    postal = line.split()[-1]
    country_code = "US"
    phone = (
        "".join(tree.xpath("//p[@class='locationPhone']/text()"))
        .replace("Phone:", "")
        .strip()
    )
    latitude = "".join(tree.xpath("//div[@data-lat]/@data-lat"))
    longitude = "".join(tree.xpath("//div[@data-lat]/@data-long"))

    return SgRecord(
        locator_domain=locator_domain,
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        phone=phone,
        latitude=latitude,
        longitude=longitude,
    )


def fetch_data():
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            if row:
                yield row


def scrape():
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1


if __name__ == "__main__":
    locator_domain = "https://bigfootjava.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }
    scrape()
