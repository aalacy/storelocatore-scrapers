import json
import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://rexel.be/filialen/")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[./span/span[contains(text(), 'Meer')]]/@href")


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text.replace("og:description", "description"))

    location_name = " ".join("".join(tree.xpath("//h1/text()")).split())
    line = tree.xpath(
        "//span[./span[contains(text(), 'Adres')]]/following-sibling::p[1]/text()"
    )
    line = list(filter(None, [l.strip().replace("\xa0", " ") for l in line]))

    if len(line) == 1:
        text = line[0]
        p = re.findall(r"\d{4}", text).pop()
        line = text.split(p)
        line[1] = f"{p}{line[1]}"

    street_address = line.pop(0).strip()
    csz = line.pop()
    if " " not in csz:
        postal = street_address.split()[-1]
        street_address = street_address.replace(postal, "").strip()
    else:
        postal = csz.split()[0]
    city = csz.replace(postal, "").strip()
    phone = (
        "".join(
            tree.xpath(
                "//span[./span[contains(text(), 'Telefoon')]]/following-sibling::p[1]/text()"
            )
        )
        .replace("/", " ")
        .strip()
    )

    try:
        text = "".join(tree.xpath("//script[contains(text(), 'addresses:')]/text()"))
        text = text.split("addresses: [")[1].split("],")[0]
        j = json.loads(text)
        latitude = j.get("latitude")
        longitude = j.get("longitude")
    except:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    _tmp = []
    hours = tree.xpath(
        "//span[./span[contains(text(), 'Openingsuren')]]/following-sibling::p[1]/text()"
    )
    for h in hours:
        if not h.strip():
            continue
        if "bureau" in h or "cash" in h:
            break
        _tmp.append(h.strip())

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code="BE",
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://rexel.be/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
