import csv

from concurrent import futures
from lxml import html
from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )

        for row in data:
            writer.writerow(row)


def get_cats():
    session = SgRequests()
    r = session.get("https://www.aspirus.org/find-a-location")
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='view-all1']/a/@href")


def get_params(cat_url):
    params = []
    data = {}
    cat_url = f"https://www.aspirus.org{cat_url}".replace("/ahc", "")
    session = SgRequests()

    _next = "random"
    while _next:
        cnt = 0
        coords = []
        r = session.post(cat_url, data=data)
        tree = html.fromstring(r.text)

        script = "".join(tree.xpath("//script[contains(text(),'var marker;')]/text()"))
        script = (
            script.split("var marker;")[1]
            .split("infowindow = null;")[0]
            .split(".LatLng")[1:]
        )

        for s in script:
            coords.append(eval(s.split(";")[0]))

        cat = "".join(
            tree.xpath("//div[@class='breadcrumb']/span[last()]/span/text()")
        ).strip()
        links = tree.xpath("//li[@data-loc]/ul/a/@href")
        for link in links:
            params.append((f"https://www.aspirus.org{link}", cat, coords[cnt]))
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
    line = " ".join(text_list).lower().replace("pm", "pm;")
    if ("24" in line or "always" in line or "everyday" in line) and len(text_list) == 1:
        return "24 hours"
    if ("limited" in line) or ("guidelines" in line) or ("website" in line):
        return "<MISSING>"
    if "hours" in line and "call" not in line:
        return line.split("hours")[-1].strip() or "<MISSING>"

    return line


def get_data(param):
    locator_domain = "https://www.aspirus.org/"
    page_url = param[0]
    location_type = param[1]
    latitude, longitude = param[2]

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = tree.xpath("//section[@class='rel-loc']//li/p/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = ", ".join(line[:-1]).strip()
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = page_url.split("-")[-1]
    phone = (
        "".join(
            tree.xpath(
                "//strong[contains(text(), 'Phone')]/following-sibling::a[contains(@href, 'tel')][1]/text()"
            )
        ).strip()
        or "<MISSING>"
    )
    if phone != "<MISSING>":
        phone = clean_phone(phone)

    hours = tree.xpath(
        "//h3[./i[@class='fa fa-clock-o']]/following-sibling::ul//text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))
    if not hours:
        hours_of_operation = "<MISSING>"
    else:
        hours_of_operation = clean_hours(hours)

    row = [
        locator_domain,
        page_url,
        location_name,
        street_address,
        city,
        state,
        postal,
        country_code,
        store_number,
        phone,
        location_type,
        latitude,
        longitude,
        hours_of_operation,
    ]

    return row


def fetch_data():
    out = []
    params = []
    cats = get_cats()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_params, cat): cat for cat in cats}
        for future in futures.as_completed(future_to_url):
            tmp = future.result()
            for param in tmp:
                params.append(param)

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, param): param for param in params}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            if row:
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
