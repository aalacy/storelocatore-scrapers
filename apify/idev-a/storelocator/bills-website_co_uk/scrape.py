from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sglogging import SgLogSetup
from sgrequests import SgRequests
import json
import re
from lxml import html
from lxml import etree
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("bills_website__co___uk")

locator_domain = "https://bills-website.co.uk"


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa0\\xa", " ")
        .replace("\\xa0", " ")
        .replace("\\xa", " ")
        .replace("\\xae", "")
    )


def fetch_data():
    with SgRequests() as session:
        url_base_restaurants = "https://bills-website.co.uk/restaurants/"
        r = session.get(url_base_restaurants)
        data_raw = html.fromstring(r.text, "lxml")
        data_raw = data_raw.xpath(
            '//main[@class="e-site-content relative z-site-content w-full mb-auto"]'
        )
        for i in data_raw:
            data_raw_clean = etree.tostring(i, pretty_print=True)
        data_raw_clean = "".join(map(chr, data_raw_clean)).replace("\\", "")
        all_urls_endpoints = re.findall(r"/restaurants/(.*?)&quot;}", data_raw_clean)
        all_urls = [url_base_restaurants + url for url in all_urls_endpoints]
        for page_url in all_urls:
            soup = bs(session.get(page_url).text, "lxml")
            _ = json.loads(
                soup.select_one("page-builder")[":header"].replace("&quot;", "")
            )
            addr = parse_address_intl(_["meta"][0]["content"])
            com = json.loads(
                soup.select_one("page-builder")[":components"]
                .replace("&quot;", '"')
                .replace("&lt;", "<")
                .replace("&gt;", ">")
                .replace("&amp;", "&")
                .replace("&amp;", "&")
            )
            hours = []
            for hour in com[0]["value"]["hours"][0]["times"]:
                hours.append(f"{hour['title']}: {hour['content']}")
            yield SgRecord(
                page_url=page_url,
                location_name=_["title"],
                street_address=addr.street_address_1,
                city=addr.city,
                zip_postal=addr.postcode,
                country_code="uk",
                phone=_["meta"][1]["content"],
                locator_domain=locator_domain,
                hours_of_operation=_valid("; ".join(hours)),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
