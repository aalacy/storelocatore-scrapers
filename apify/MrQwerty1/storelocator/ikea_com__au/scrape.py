import re

from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.ikea.com/au/en/stores/")
    tree = html.fromstring(r.text)

    return tree.xpath("//p/a[contains(@href, 'au/en/stores/')]/@href")


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    phone = "".join(
        tree.xpath(
            "//h2[./strong[contains(text(), 'Address')]]/following-sibling::p[2]/text()"
        )
    )
    location_name = "".join(
        tree.xpath("//h1[contains(@class, 'pub__h1')]/text()")
    ).strip()
    lines = tree.xpath(
        "//h2[./strong[contains(text(), 'Address')]]/following-sibling::p[1]/text()|//p[./strong[contains(text(), 'Address')]]/following-sibling::p/text()"
    )
    lines = list(filter(None, [line.strip() for line in lines]))
    if "T:" in lines[-1]:
        phone = lines.pop()
    phone = phone.replace("T:", "").strip()
    if len(phone) > 15:
        phone = SgRecord.MISSING

    raw_address = ", ".join(lines).strip()
    if "(" in raw_address:
        raw_address = (
            raw_address[: raw_address.index("(")]
            + raw_address[raw_address.index(")") + 1 :]
        )
    raw_address = raw_address.replace(",,", ",").replace(", ,", ",")
    street_address, csz = SgRecord.MISSING, SgRecord.MISSING
    for li in lines:
        if li[0].isdigit():
            street_address = li
            continue
        if re_state.findall(li) or re_postal.findall(li):
            csz = li

    if street_address == SgRecord.MISSING:
        street_address = lines[0]

    if street_address.endswith(","):
        street_address = street_address[:-1]
    state = "".join(re_state.findall(csz))
    postal = "".join(re_postal.findall(csz))
    city = csz.replace(postal, "").replace(state, "").strip()

    text = "".join(tree.xpath("//a[contains(@href, 'google')]/@href|//iframe/@src"))
    if "/@" in text:
        latitude = text.split("@")[1].split(",")[0]
        longitude = text.split("@")[1].split(",")[1]
    elif "embed?" in text:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    else:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    hours = tree.xpath(
        "//h4[./strong[contains(text(), 'Store')]]/following-sibling::p/text()|//h3[./strong[contains(text(), 'Store')]]/following-sibling::p/text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))
    hours_of_operation = ";".join(hours)

    if not hours:
        _tmp = []
        _hours = tree.xpath(
            "//p[./strong[contains(text(), 'Hours')]]/following-sibling::p"
        )
        for h in _hours:
            day = "".join(h.xpath("./strong/text()")).strip()
            inter = "".join(h.xpath("./text()")).replace("-", "").strip()
            if not inter:
                continue
            _tmp.append(f"{day}: {inter}")

        hours_of_operation = ";".join(_tmp)

    if ";*" in hours_of_operation:
        hours_of_operation = hours_of_operation.split(";*")[0].strip()

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="AU",
        phone=phone,
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    re_state = re.compile(r"[A-Z]{2,3}")
    re_postal = re.compile(r"\d{4}")
    locator_domain = "https://www.ikea.com/au"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
