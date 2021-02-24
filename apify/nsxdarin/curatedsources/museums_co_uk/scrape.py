# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("museums_co_uk")


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
                "raw_address",
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


def fetch_data():
    locs = []
    url = "https://www.museums.co.uk/jm-ajax/get_listings/?lang=&search_keywords=&search_location=&search_categories%5B%5D=&filter_job_type%5B%5D=freelance&filter_job_type%5B%5D=full-time&filter_job_type%5B%5D=internship&filter_job_type%5B%5D=part-time&filter_job_type%5B%5D=temporary&filter_job_type%5B%5D=&per_page=2000&orderby=featured&order=DESC&page=1&show_pagination=false&form_data=search_keywords%3D%26search_location%3D%26search_categories%255B%255D%3D%26search_region%3D%26filter_job_type%255B%255D%3Dfreelance%26filter_job_type%255B%255D%3Dfull-time%26filter_job_type%255B%255D%3Dinternship%26filter_job_type%255B%255D%3Dpart-time%26filter_job_type%255B%255D%3Dtemporary%26filter_job_type%255B%255D%3D"
    r = session.get(url, headers=headers, timeout=90)
    website = "museums.co.uk"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'data-permalink=\\"' in line:
            items = line.split('data-permalink=\\"')
            for item in items:
                if '{"found_jobs":true' not in item:
                    locs.append(
                        item.split('"\\n\\t         data-categories')[0].replace(
                            "\\", ""
                        )
                    )
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = "<MISSING>"
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        hours = "<MISSING>"
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if 'property="og:title" content="' in line2:
                name = line2.split('property="og:title" content="')[1].split('"')[0]
            if 'data-latitude="' in line2:
                lat = line2.split('data-latitude="')[1].split('"')[0]
            if 'data-longitude="' in line2:
                lng = line2.split('data-longitude="')[1].split('"')[0]
            if 'address_icon"></i>' in line2:
                rawadd = (
                    line2.split('address_icon"></i>')[1]
                    .split("<")[0]
                    .replace(", UK", "")
                    .replace(", United Kingdom", "")
                )
                addr = parse_address_intl(rawadd)
                city = addr.city
                zc = addr.postcode
                add = addr.street_address_1
            if 'hone"></i>' in line2:
                phone = line2.split('hone"></i>')[1].split("<")[0].strip()
        hours = "<MISSING>"
        if add == "" or add is None:
            add = "<MISSING>"
        if city == "" or city is None:
            city = "<MISSING>"
        if zc == "" or zc is None:
            zc = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        name = name.replace("ʼ", "'")
        city = city.replace("ʼ", "'")
        add = add.replace("ʼ", "'")
        yield [
            website,
            loc,
            name,
            rawadd,
            add,
            city,
            state,
            zc,
            country,
            store,
            phone,
            typ,
            lat,
            lng,
            hours,
        ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
