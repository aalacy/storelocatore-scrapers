from lxml import html
from typing import List
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def get_urls():
    r = session.get("https://www.rightathomecanada.com/about-us/locations")
    tree = html.fromstring(r.text)

    return set(
        tree.xpath("//div[@class='para']//a[not(contains(@href, 'tel:'))]/@href")
    )


def write(data: dict, sgw: SgWriter):
    row = SgRecord(
        page_url=data.get("page_url"),
        location_name=data.get("location_name"),
        street_address=data.get("street_address"),
        city=data.get("city"),
        state=data.get("state"),
        zip_postal=data.get("postal"),
        country_code="CA",
        phone=data.get("phone"),
        locator_domain=locator_domain,
        raw_address=data.get("raw_address"),
    )

    sgw.write_row(row)


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.rightathomecanada.com{slug}"
    if "-kent" in page_url:
        return
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = tree.xpath("//h1/text()")[0].strip()
    phone = "".join(
        tree.xpath(
            "//button[contains(@aria-label, 'search')]/preceding-sibling::a/text()"
        )
    ).strip()
    street_address, city = SgRecord.MISSING, SgRecord.MISSING
    state, postal = SgRecord.MISSING, SgRecord.MISSING
    raw_address = SgRecord.MISSING

    data = {
        "page_url": page_url,
        "location_name": location_name,
        "phone": phone,
        "street_address": street_address,
        "city": city,
        "state": state,
        "postal": postal,
        "raw_address": raw_address,
    }

    line = tree.xpath(
        "//ul[.//a[contains(text(), 'Contact Us')]]/preceding-sibling::div[@class='para']//text()"
    )
    line = list(
        filter(None, [l.replace("\xa0", " ").replace("\t", " ").strip() for l in line])
    )
    if len(line) > 1:
        try:
            line = line[: line.index("Phone:")]
        except:
            cnt = 0
            for li in line:
                if "Phone:" in li:
                    break
                cnt += 1
            line = line[:cnt]
        if "Right" in line[0] or "Greater" in line[0]:
            line.pop(0)
        for li in line:
            if "Right" in li:
                ismultiple = True
                break
        else:
            ismultiple = False

        if not ismultiple:
            raw_address = " ".join(line)
            street_address, city, state, postal = get_international(raw_address)
            data["street_address"] = street_address
            data["city"] = city
            data["state"] = state
            data["postal"] = postal
            data["raw_address"] = raw_address
            write(data, sgw)
        else:
            _tmp = []  # type: List[str]
            records = []
            for li in line:
                if "Right" in li:
                    records.append(_tmp)
                    _tmp = []
                _tmp.append(li)
            else:
                records.append(_tmp)

            for record in records:
                if "Right" in record[0]:
                    data["location_name"] = record.pop(0)
                raw_address = " ".join(record)
                street_address, city, state, postal = get_international(raw_address)
                if state in postal:
                    postal = postal.replace(state, "").strip()
                data["street_address"] = street_address
                data["city"] = city
                data["state"] = state
                data["postal"] = postal
                data["raw_address"] = raw_address
                write(data, sgw)
    else:
        write(data, sgw)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.rightathomecanada.com/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
