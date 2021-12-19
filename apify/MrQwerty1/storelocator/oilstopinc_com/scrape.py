import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def clean_phone(text):
    out = []
    if text.find("|") != -1:
        text = text.split("|")[0].strip()

    for t in text:
        if t.isdigit():
            out.append(t)

    return "(" + "".join(out[:3]) + ") " + "".join(out[3:6]) + "-" + "".join(out[6:])


def get_urls():
    r = session.get("https://oilstopinc.com/locations/", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//td[@class='locations-indent']/a[contains(@href, 'oil-') and ./text()]/@href"
    )


def get_data(page_url, sgw: SgWriter):
    if page_url.startswith("/"):
        page_url = f"https://oilstopinc.com{page_url}"

    r = session.get(page_url, headers=headers)
    try:
        tree = html.fromstring(r.text)
    except:
        return
    location_name = "".join(tree.xpath("//h1/text()")).replace("\n", "").strip()
    line = tree.xpath("//*[@class='tlocations']//text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = SgRecord.MISSING
    phone = SgRecord.MISSING
    part = ""
    hours = ""
    for l in line:
        if (
            l[0].isdigit()
            and l.find("reviews") == -1
            and not re.findall(r"(\d{3}-\d{4})", l)
        ):
            street_address = l
        if re.findall(r"(\d{3}-\d{4})", l):
            phone = clean_phone(l)
        if re.findall(r"\d{5}", l):
            part = l
        if l.find("Open") != -1:
            hours = l.replace("Open", "").replace(" / ", ";").replace(", ", ";").strip()
            if hours.find("|") != -1:
                hours = hours.split("|")[-1].strip()

    city = part.split(",")[0].strip()
    part = part.split(",")[1].strip()
    state = part.split()[0]
    postal = part.split()[1]
    country_code = "US"
    hours_of_operation = hours
    if ")" in hours_of_operation:
        hours_of_operation = SgRecord.MISSING

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        phone=phone,
        country_code=country_code,
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
    locator_domain = "https://oilstopinc.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
