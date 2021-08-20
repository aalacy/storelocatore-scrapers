import csv
import re

from lxml import (
    etree,
    html,
)

from sgrequests import SgRequests

domain_name = "sandellasusa.com"


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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


def xpath(hxt, query_string):
    hxp = hxt.xpath(query_string)
    if hxp:
        if hasattr(hxp[0], "encode"):
            return hxp[0].encode("utf-8")
        return hxp[0]
    return None


def extract(row):

    re_address = re.compile(r"([A-Z0-9]+) ([ \.A-Z0-9a-z]+) ([A-Z0-9a-z\.]+)")

    name = xpath(row, ".//span//text()").decode("utf-8").strip()
    text = etree.tostring(row).decode("utf-8")
    text = re.sub("&#8217;|&nbsp;|&#160;", "", text)

    street_address = None
    street_address_matches = re.findall(re_address, text)
    if street_address_matches:
        street_address = " ".join(street_address_matches[0])

    if not street_address:
        street_suny_match = re.match(r"Johnson Rd\. Commissary Bldg\.", text)
        if street_suny_match:
            street_address = street_suny_match.group(0)

    if not street_address:
        street_rensselaer_match = re.match(r"15th and Sage Avenue", text)
        if street_rensselaer_match:
            street_address = street_rensselaer_match.group(0)

    if not street_address:
        street_address = None

    second_line = etree.tostring(row[1], pretty_print=True).decode("utf-8")
    # if the second paragraph doesn't match the street address pattern
    # and it's not equal to the value of street_address, then treat it as the first line of the address
    if not re.match(re_address, second_line):
        address_first_line = xpath(row[1], ".//span//text()").strip().decode("utf-8")
        if street_address and street_address not in address_first_line:
            street_address = address_first_line + " - " + street_address
        else:
            street_address = address_first_line

    try:
        street_address = street_address.split("-")[1].strip()
    except:
        pass

    city, state, zipcode = None, None, None
    region = re.findall(r"([A-Za-z]+)(,|) ([A-Z,]+) ([0-9]+)", text)
    if region:
        city, _, state, zipcode = region[0]

    state = state.replace(",", "")

    phone = re.findall(r"\d+-\d+-\d+", text)
    phone = phone[0] if phone else "<MISSING>"

    return [
        domain_name,
        "https://sandellasusa.com/locations",
        name,
        street_address,
        city,
        state,
        zipcode,
        "US",
        "<MISSING>",
        phone,
        "<MISSING>",
        "<MISSING>",
        "<MISSING>",
        "<MISSING>",
    ]


def fetch_data():

    url = "https://sandellasusa.com/locations"

    data = []

    session = SgRequests()
    session.get_session().headers.update(
        {
            "authority": "sandellasusa.com",
            "method": "GET",
            "path": "/locations",
            "scheme": "https",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9,it;q=0.8",
            "cache-control": "max-age=0",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36)",
        }
    )
    request = session.get(url)
    if request.status_code == 200:
        rows = html.fromstring(request.text).xpath('//div[@data-ux="ContentText"]')
        for row in rows:
            if xpath(row, ".//span//text()") is None:
                continue
            row_text = etree.tostring(row).decode("utf-8")
            sub_rows = re.split(
                '<p style="margin:0"><span><br/></span></p>|<p style="margin:0"><span>&#8203;</span></p>',
                row_text,
            )

            if len(sub_rows) == 1:
                row = etree.fromstring(sub_rows[0])
                data.append(extract(row))
            else:
                for i, sub_row in enumerate(sub_rows):
                    if i == 0:
                        valid_html = sub_row + "</div>"
                    elif i == len(sub_rows) - 1:
                        valid_html = "<div>" + sub_row
                    else:
                        valid_html = "<div>" + sub_row + "</div>"

                    row = etree.fromstring(valid_html)
                    if len(row) > 0:
                        data.append(extract(row))
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
