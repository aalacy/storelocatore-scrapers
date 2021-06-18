import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import dirtyjson as json
import re
from sgscrape.sgpostal import parse_address_intl


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
                "brand_website",
                "raw_address",
            ]
        )
        # Body
        for row in data:
            if row:
                writer.writerow(row)


logger = SgLogSetup().get_logger("findawarehouse")

_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.5",
    "Content-Type": "application/x-www-form-urlencoded",
    "Host": "www.findawarehouse.org",
    "Origin": "https://www.findawarehouse.org",
    "Referer": "https://www.findawarehouse.org/SearchFAW",
    "Content-Length": "9570",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
}

ca_provinces_codes = {
    "AB",
    "BC",
    "MB",
    "NB",
    "NL",
    "NS",
    "NT",
    "NU",
    "ON",
    "PE",
    "QC",
    "SK",
    "YT",
}


_header1 = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


locator_domain = "https://www.findawarehouse.org/"
base_url = "https://www.findawarehouse.org/SearchFAW"
urls = []


def _ll(street, json_locations):
    latitude = longitude = phone = ""
    for loc in json_locations:
        if street in loc["Address"]:
            latitude = loc["Lat"]
            longitude = loc["Lng"]
            phone = loc["Phone"]

    return latitude, longitude, phone


def get_country_by_code(code=""):
    if code in ca_provinces_codes:
        return "CA"
    else:
        return "US"


def _detail(_, json_locations, session):
    name = _.h2.text.strip()
    page_url = f"https://www.findawarehouse.org/DetailsHD.aspx?company={name.replace(' ', '%20')}"
    if page_url in urls:
        return []
    urls.append(page_url)
    _addr = list(_.p.stripped_strings)
    if _addr[0] == _.p.b.text.strip():
        del _addr[0]
    latitude, longitude, phone = _ll(_addr[0], json_locations)
    addr = parse_address_intl(" ".join(_addr[:2]))
    street_address = addr.street_address_1
    if addr.street_address_2:
        street_address += " " + addr.street_address_2
    brand_website = ""
    if _addr[-1].startswith("http"):
        brand_website = _addr[-1]
    return [
        locator_domain,
        page_url,
        name,
        street_address or "<MISSING>",
        addr.city.replace(",", ""),
        addr.state,
        addr.postcode,
        get_country_by_code(addr.state),
        "<MISSING>",
        phone,
        "<MISSING>",
        latitude,
        longitude,
        "<MISSING>",
        brand_website,
        " ".join(_addr[:2]),
    ]


def fetch_data():
    _data = []
    with SgRequests() as session:
        total = 0
        res = session.get(base_url, headers=_header1).text
        soup = bs(res, "lxml")
        json_locations = json.loads(res.split("JSON.parse('")[1].split("');")[0])
        locations = soup.select("div.srch-res-l")
        total += len(locations)
        logger.info(f"[total {total}] {len(locations)} found")
        for _ in locations:
            _data.append(_detail(_, json_locations, session))
        while True:
            __VIEWSTATE = soup.select_one("input#__VIEWSTATE")["value"]
            __VIEWSTATEGENERATOR = soup.select_one("input#__VIEWSTATEGENERATOR")[
                "value"
            ]
            __EVENTVALIDATION = soup.select_one("input#__EVENTVALIDATION")["value"]
            _next = soup.find("a", string=re.compile(r"next"))
            if not _next:
                break
            __EVENTTARGET = _next["href"].replace("javascript:__doPostBack('", "")[:-5]
            data = {
                "__EVENTTARGET": __EVENTTARGET,
                "__EVENTARGUMENT": "",
                "__VIEWSTATE": __VIEWSTATE,
                "__VIEWSTATEGENERATOR": __VIEWSTATEGENERATOR,
                "__EVENTVALIDATION": __EVENTVALIDATION,
                "ctl00$MainContent$Repeater1$ctl01$hfName": "24/7+Enterprises,+LLC",
                "ctl00$MainContent$Repeater1$ctl01$hfEmail": "abaptiste@247csl.com",
                "ctl00$MainContent$Repeater1$ctl02$hfName": "307+Warehousing+and+Logistics",
                "ctl00$MainContent$Repeater1$ctl02$hfEmail": "rlstoddard@307corp.com",
                "ctl00$MainContent$Repeater1$ctl03$hfName": "3rd+Party+Logistics+Group+of+NJ,+Inc.",
                "ctl00$MainContent$Repeater1$ctl03$hfEmail": "",
                "ctl00$MainContent$Repeater1$ctl04$hfName": "A.+Hartrodt",
                "ctl00$MainContent$Repeater1$ctl04$hfEmail": "miriam.wohlen@hartrodt.com",
                "ctl00$MainContent$Repeater1$ctl05$hfName": "A.+Hartrodt",
                "ctl00$MainContent$Repeater1$ctl05$hfEmail": "miriam.wohlen@hartrodt.com",
                "ctl00$MainContent$Repeater1$ctl06$hfName": "a2b+Fulfillment,+Inc.",
                "ctl00$MainContent$Repeater1$ctl06$hfEmail": "",
                "ctl00$MainContent$Repeater1$ctl07$hfName": "Ability/Tri-Modal+and+City",
                "ctl00$MainContent$Repeater1$ctl07$hfEmail": "",
                "ctl00$MainContent$Repeater1$ctl08$hfName": "ACCEM+Warehouse",
                "ctl00$MainContent$Repeater1$ctl08$hfEmail": "",
                "ctl00$MainContent$Repeater1$ctl09$hfName": "Accem+Warehouse+-+Global+Terminal",
                "ctl00$MainContent$Repeater1$ctl09$hfEmail": "alex.mecca@accem.com",
                "ctl00$MainContent$Repeater1$ctl10$hfName": "Access+Plus+Warehouse+&+Logistics",
                "ctl00$MainContent$Repeater1$ctl10$hfEmail": "",
            }

            res1 = session.post(base_url, headers=_headers, data=data).text
            soup = bs(res1, "lxml")
            json_locations = json.loads(res1.split("JSON.parse('")[1].split("');")[0])
            locations = soup.select("div.srch-res-l")
            total += len(locations)
            logger.info(f"[total {total}] {len(locations)} found")
            for _ in locations:
                _data.append(_detail(_, json_locations, session))

        return _data


def scrape():
    write_output(fetch_data())


if __name__ == "__main__":
    scrape()
