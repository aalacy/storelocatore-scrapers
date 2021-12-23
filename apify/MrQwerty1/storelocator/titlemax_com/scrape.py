from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.titlemax.com/addl-sitemap.xml", headers=headers)
    tree = html.fromstring(str(r.content).replace("<![CDATA[", "").replace("]]>", ""))
    return tree.xpath("//loc/text()")


def get_data(page_url, sgw: SgWriter):
    try:
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
    except:
        return

    try:
        sect = tree.xpath("//section[@id='store-info']")[0]
    except IndexError:
        return
    location_name = "".join(tree.xpath("//h1[@itemprop='name']/text()")).strip()
    line = sect.xpath("//div[@itemprop='address']/text()")
    line = list(filter(None, [l.strip() for l in line]))
    street_address = ", ".join(line[:-1])
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[-1].strip()
    state = line.split()[0]
    postal = line.split()[-1]
    country_code = "US"
    phone = "".join(sect.xpath(".//span[@itemprop='telephone']/text()")).strip()
    if page_url.find("pawns") != -1:
        location_type = "Title Pawns"
    elif page_url.find("loans") != -1:
        location_type = "Title Loans"
    elif page_url.find("appraiser") != -1:
        location_type = "TitleMax Appraisals"
    else:
        location_type = "Title Loans"

    script = "".join(tree.xpath("//script[contains(text(),'L.marker')]/text()"))
    latlon = [SgRecord.MISSING, SgRecord.MISSING]
    for line in script.split("\n"):
        if line.find("L.marker") != -1:
            latlon = line.split("[")[1].split("]")[0].split(",")
            break

    latitude, longitude = latlon

    _tmp = []
    dl = sect.xpath(".//*[text()='Hours']/following-sibling::dl/div")
    for d in dl:
        day = "".join(d.xpath("./dt//text()")).strip()
        time = "".join(d.xpath("./dd//text()")).strip()
        _tmp.append(f"{day} {time}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        phone=phone,
        location_type=location_type,
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.titlemax.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Upgrade-Insecure-Requests": "1",
    }
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
