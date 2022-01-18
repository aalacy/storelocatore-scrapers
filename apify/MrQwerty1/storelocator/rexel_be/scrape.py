import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    urls = []
    r = session.get(
        "https://rexel.be/wp-json/wpgmza/v1/datatables/base64eJy1krFqwzAURf-lziokTbNoCx26NCTQQqFxKK-Wiy0qy+ZJNgGTf4-sONCtS72Jq3uPBp0eTdk8OwoBGh-7l+3nJsu2JD8srzZE64ss25iOfM7mnb4dQyFEkgi9UHDsi1hCPywVKmq+rEmUVarktWsrn5iHHoYijW1PFaf7gcAkeTnidJSWFWoxLL+DWwW6R0eunXbCBZ+hT+QCXy7qzl7OyH6ckb2akf00I3v9-+zjNBuNudkz-quxKQKFHEPlb5DCybrIksTdk1CVFOxTWHcsYg1PTu+Gp944Dudwn14BTzQDrw"
    )
    for j in r.json()["meta"]:
        text = j.get("link") or "<html></html>"
        tree = html.fromstring(text)
        url = "".join(tree.xpath("//a/@href"))
        if url.startswith("/"):
            url = f"https://rexel.be{url}"
        urls.append(url)

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text.replace("og:description", "description"))

    location_name = " ".join("".join(tree.xpath("//h2//text()")).split())
    if "KNX" in location_name:
        location_name = location_name.split("KNX")[0].strip()
    line = tree.xpath("//p[./strong[contains(text(), 'Adres')]]//text()")
    line = list(filter(None, [l.strip().replace("\xa0", " ") for l in line]))

    line.pop(0)
    if "REXEL" in line[0] or "HAVEN" in line[0]:
        line.pop(0)
    if len(line) == 3 and "(" not in line[1]:
        line[-1] = " ".join(line[1:])
    if "WEYLER" in line[-1]:
        line[-1] = line[-1].split("WEYLER")[-1].strip()

    street_address = line.pop(0).strip()
    csz = line.pop()
    postal = csz.split()[0]
    city = csz.replace(postal, "").strip()
    phone = (
        tree.xpath("//strong[contains(text(), 'Tel:')]/following-sibling::text()")[0]
        .replace("/", " ")
        .strip()
    )
    if "(" in phone:
        phone = phone.split("(")[0].strip()

    try:
        text = "".join(tree.xpath("//script[contains(text(), 'addresses:')]/text()"))
        text = text.split("addresses: [")[1].split("],")[0]
        j = json.loads(text)
        latitude = j.get("latitude")
        longitude = j.get("longitude")
    except:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    try:
        _tmp = []
        write = False
        source = "".join(tree.xpath("//meta[@property='description']/@content"))
        for line in source.split("\r\n"):
            if "openingsuren" in line.lower():
                write = True
                continue
            if (
                "commercieel" in line.lower()
                or "tel:" in line.lower()
                or "cash" in line
            ):
                break
            if write:
                _tmp.append(line.strip())
        hours_of_operation = ";".join(_tmp).replace("/", "|").replace("u", ":")
    except:
        hours_of_operation = SgRecord.MISSING

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
