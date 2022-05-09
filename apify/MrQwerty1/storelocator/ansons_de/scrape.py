from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_ids():
    r = session.get("https://www.ansons.de/standorte/", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@data-store-id]/@data-store-id")


def get_phone(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    phone = "".join(tree.xpath("//p[contains(text(), 'Telefon')]/text()")).strip()
    phone = phone.replace("Telefon", "").replace(":", "").strip()

    return phone


def get_data(store_number, sgw: SgWriter):
    page_url = f"https://www.ansons.de/standorte/haus-{store_number}/"
    api = f"https://www.ansons.de/storefinder/get-store-data/{store_number}/"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)

    location_name = tree.xpath("//h2[@class='storeInfos-headline']/text()")[0].strip()
    b = tree.xpath("//p[@class='storeInfos-text']/span")[0]
    street_num = "".join(b.xpath("./text()"))
    street_nam = "".join(b.xpath("./preceding-sibling::text()")).strip()
    street_address = f"{street_nam} {street_num}".strip()
    cz = "".join(b.xpath("./following-sibling::text()")).replace("\xa0", " ").strip()
    postal = cz.split()[0]
    city = cz.replace(postal, "").strip()
    country_code = "DE"
    try:
        phone = get_phone(page_url)
    except:
        phone = SgRecord.MISSING

    latitude = "".join(tree.xpath("//div/@data-map-lat"))
    longitude = "".join(tree.xpath("//div/@data-map-lon"))

    hours = tree.xpath(
        f"//div[contains(@id, '{store_number}-store')]//ul[@class='storeInfos-openingHours']/li/text()"
    )
    hours_of_operation = ";".join(hours)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    ids = get_ids()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, _id, sgw): _id for _id in ids}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.ansons.de/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        get_data("135", writer)
        fetch_data(writer)
