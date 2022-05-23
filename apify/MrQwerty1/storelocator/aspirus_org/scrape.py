from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_params():
    params = []
    data = dict()

    _next = "random"
    while _next:
        cnt = 0
        coords = []
        r = session.post("https://www.aspirus.org/find-a-location", data=data)
        tree = html.fromstring(r.text)

        try:
            script = "".join(
                tree.xpath("//script[contains(text(),'var marker;')]/text()")
            )
            script = (
                script.split("var marker;")[1]
                .split("infowindow = null;")[0]
                .split(".LatLng")[1:]
            )

            for s in script:
                coords.append(eval(s.split(";")[0]))
        except:
            pass

        links = tree.xpath("//li[@data-loc]/a/@href")
        for link in links:
            try:
                coord = coords[cnt]
            except IndexError:
                coord = (SgRecord.MISSING, SgRecord.MISSING)
            params.append((f"https://www.aspirus.org{link}", coord))
            cnt += 1

        _next = "".join(
            tree.xpath(
                "//span[@id='cphBody_cphCenter_ctl01_PaginationTop']/div/a[@class='aspNetDisabled cpsty_PagerCurrentPage']/following-sibling::a[1]/@href"
            )
        )
        if not _next:
            return params

        _next = _next.split("'")[1]
        _state = "".join(tree.xpath("//input[@id='__VIEWSTATE']/@value"))
        _validation = "".join(tree.xpath("//input[@id='__EVENTVALIDATION']/@value"))
        data = {
            "__EVENTTARGET": _next,
            "__VIEWSTATE": _state,
            "__EVENTVALIDATION": _validation,
            "ctl00$ctl00$FormAction": "ExecuteSearch",
        }


def clean_phone(text):
    _tmp = []
    for t in text:
        if t.isdigit() and len(_tmp) != 10:
            _tmp.append(t)

    if len(_tmp) < 10:
        return "<MISSING>"

    _tmp.insert(3, "-")
    _tmp.insert(7, "-")

    return "".join(_tmp)


def clean_hours(text_list):
    if text_list[0] == "Business Hours":
        text_list = text_list[1:]
    line = " ".join(text_list).lower().replace("pm", "pm;")
    if "holidays:" in line:
        line = line.split("holidays")[0].strip()
    if "hospice" in line:
        line = line.split("hospice")[0].strip()
    if "after-hours" in line:
        line = line.split("after-hours")[0].strip()
    if "evenings by appointment" in line:
        line = line.split("evenings by appointment")[0].strip()
    if "rehab services" in line:
        line = line.split("rehab services")[0].strip()
    if "holidays closed" in line:
        line = line.split("holidays closed")[0].strip()

    if ("24" in line or "always" in line or "everyday" in line) and len(text_list) <= 2:
        return "24 hours"
    if (
        ("limited" in line)
        or ("guidelines" in line)
        or ("website" in line)
        or ("open by appointment" in line)
    ):
        return "<MISSING>"
    if "hours" in line and "call" not in line:
        return line.split("hours")[-1].strip() or "<MISSING>"

    return line


def get_data(param, sgw: SgWriter):
    page_url = param[0]
    latitude, longitude = param[1]

    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    if " - " in location_name:
        location_name = location_name.split(" - ")[0].strip()
    line = tree.xpath("//section[@class='rel-loc']//li/p/text()")
    line = list(filter(None, [l.strip() for l in line]))

    if line:
        street_address = ", ".join(line[:-1]).strip()
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
    else:
        street_address = SgRecord.MISSING
        city = SgRecord.MISSING
        state = SgRecord.MISSING
        postal = SgRecord.MISSING

    if street_address == SgRecord.MISSING and city == SgRecord.MISSING:
        return
    store_number = page_url.split("-")[-1]
    phone = "".join(
        tree.xpath(
            "//strong[contains(text(), 'Phone')]/following-sibling::a[contains(@href, 'tel')][1]/text()"
        )
    ).strip()
    if phone:
        phone = clean_phone(phone)

    hours = tree.xpath(
        "//h3[./i[@class='fa fa-clock-o']]/following-sibling::ul//text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))
    if not hours:
        hours_of_operation = SgRecord.MISSING
    else:
        hours_of_operation = clean_hours(hours).replace("closed on holidays", "")

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="US",
        store_number=store_number,
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    params = get_params()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {
            executor.submit(get_data, param, sgw): param for param in params
        }
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.aspirus.org/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
