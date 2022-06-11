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


def get_ids():
    session = SgRequests()
    r = session.get("https://www.justtyres.co.uk/find-a-fitter")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//select[@id='InnerPH_InnerPH_findFitterId_ddl_fitting_centre']/option[not(@selected)]/@value"
    )


def get_data(_id):
    locator_domain = "https://www.justtyres.co.uk/"
    page_url = "<MISSING>"

    data = {"jt-fitter-center": _id, "jt-range": "30", "action": "render_fitter_result"}

    session = SgRequests()
    r = session.post("https://www.justtyres.co.uk/ControlsApi.ashx", data=data)
    tree = html.fromstring(r.text)

    line = tree.xpath("//p[@id='rpt_centre_results_centre_address_0']/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = ", ".join(line[:-2])
    city = line[-2]
    state = "<MISSING>"
    postal = line[-1]
    country_code = "GB"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//a[@id='rpt_centre_results_fitter_number_0']/text()"))
        .replace("Call:", "")
        .strip()
        or "<MISSING>"
    )
    latitude, longitude = "".join(
        tree.xpath("//input[@id='rpt_centre_results_centre_geo_0']/@value")
    ).split(",")
    location_type = "<MISSING>"

    _tmp = []
    days = tree.xpath(
        "//div[@id='rpt_centre_results_centre_stats_0']//p[text()='Opening times']/following-sibling::p[1]/text()"
    )[:-1]
    times = tree.xpath(
        "//div[@id='rpt_centre_results_centre_stats_0']//p[text()='Opening times']/following-sibling::p[1]/span/text()"
    )[:-1]

    for d, t in zip(days, times):
        if t.lower().find("closed - closed") != -1:
            t = "Closed"
        _tmp.append(f"{d.strip()} {t.strip()}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    location_name = city

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
    ids = get_ids()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, _id): _id for _id in ids}
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
