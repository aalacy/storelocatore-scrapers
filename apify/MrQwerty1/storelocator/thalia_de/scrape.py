from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.thalia.de/shop/home/filialen/", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//ul[@class='menu vertical']/li/a/@href")


def get_data(api, sgw: SgWriter):
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)

    coords = []
    text = "".join(tree.xpath("//script[contains(text(), 'latlng')]/text()"))
    text = text.split("latlng:")
    text.pop(0)
    for t in text:
        lat = t.split("b:")[1].split(",")[0].strip()
        lng = t.split("l:")[1].split("}")[0].strip()
        coords.append((lat, lng))

    divs = tree.xpath("//div[@class='row ncItem boxSimple']")

    for d, c in zip(divs, coords):
        location_name = " ".join(
            " ".join(d.xpath(".//a[@data-test='filialeName']//text()")).split()
        )
        page_url = "".join(d.xpath(".//a[@data-test='filialeName']/@href"))
        street_address = "".join(d.xpath(".//span[@class='oStreet']/text()")).strip()
        city = "".join(d.xpath(".//span[@class='oCity']/text()")).strip()
        postal = "".join(d.xpath(".//span[@class='oZipCode']/text()")).strip()
        country_code = "DE"
        phone = "".join(d.xpath(".//span[@class='oPhone']/a/text()")).strip()
        store_number = page_url.split("/")[-2]
        latitude, longitude = c

        _tmp = []
        hours = d.xpath(
            ".//dt[./h4[contains(text(), 'Öffnungszeiten')]]/following-sibling::dd"
        )
        for h in hours:
            day = "".join(h.xpath("./div[1]/text()")).strip()
            inter = "".join(h.xpath("./div[2]/text()")).strip()
            _tmp.append(f"{day}: {inter}")

        hours_of_operation = ";".join(_tmp)

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
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.thalia.de/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
