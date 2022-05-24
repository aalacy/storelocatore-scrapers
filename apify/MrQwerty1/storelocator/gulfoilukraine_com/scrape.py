from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING

    return street, city


def get_urls():
    r = session.get("https://gulfoilukraine.com/partners_category/", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//select[@class='select_partners']/option[@value]/@value")


def get_data(slug, sgw: SgWriter):
    page_url = f"https://gulfoilukraine.com/partners_category/{slug}/"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='partner_block']")

    for d in divs:
        location_name = "".join(d.xpath(".//p[@class='name_partners']/text()")).strip()
        line = d.xpath(".//p[img]/text()")
        line = list(filter(None, [li.strip() for li in line]))
        raw_address = line.pop(0)
        sep = ["вул.", "бульв.", "просп.", "вулиця", "перевулок"]
        for s in sep:
            if s in raw_address:
                city = raw_address.split(s)[0].strip()
                street_address = raw_address.replace(city, "").strip()
                break
        else:
            street_address, city = get_international(raw_address)

        if street_address == "М.":
            street_address = SgRecord.MISSING
            city = raw_address
        if "М. Харків" in street_address:
            street_address = street_address.replace("М. Харків", "").strip()
            city = "м. Харків"

        city = city.replace("СТО", "").replace("Авторинок", "")
        if ";" in city:
            city = city.split(";")[0].strip()
        if " Новоселицький " in city:
            city = city.split(" Новоселицький ")[0]
        if city.endswith(","):
            city = city[:-1].strip()

        state = "".join(tree.xpath("//option[@selected]/text()")).strip()
        country_code = "UA"
        phone = line.pop(0).replace("(Viber)", "").replace("(WhatsApp)", "").strip()
        if "." in phone:
            phone = phone.split(".")[0].strip()
        if "," in phone:
            phone = phone.split(",")[1].strip()

        latitude = "".join(d.xpath(".//div[@data-lat]/@data-lat"))
        longitude = "".join(d.xpath(".//div[@data-lat]/@data-lng"))

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            raw_address=raw_address,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://gulfoilukraine.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
