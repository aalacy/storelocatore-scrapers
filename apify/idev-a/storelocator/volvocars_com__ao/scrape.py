from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re
import json
from sgpostal.sgpostal import parse_address_intl
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.volvocars.com/ao"
urls = {
    "Namibia": "https://www.volvocars.com/na",
    "Angola": "https://www.volvocars.com/ao",
    "Ecuador": "https://www.volvocars.com/ec",
    "Zambia": "https://www.volvocars.com/zm",
    "Zimbabwe": "https://www.volvocars.com/zw",
}


def _d(country, base_url, location_name, raw_address, phone, hours="", lat="", lng=""):
    raw_address = raw_address.replace("\xa0", "")
    if country not in raw_address:
        raw_address + ", " + country
    addr = parse_address_intl(raw_address)
    street_address = addr.street_address_1
    if addr.street_address_2:
        street_address += " " + addr.street_address_2
    return SgRecord(
        page_url=base_url,
        location_name=location_name.replace(":", " "),
        street_address=street_address,
        city=addr.city,
        state=addr.state,
        zip_postal=addr.postcode,
        country_code=country,
        phone=phone.split(":")[-1].replace("\xa0", ""),
        latitude=lat.strip(),
        longitude=lng.strip(),
        locator_domain=locator_domain,
        hours_of_operation=hours,
        raw_address=raw_address,
    )


def fetch_data():
    with SgRequests() as session:
        for country, base_url in urls.items():
            logger.info(base_url)
            soup = bs(session.get(base_url, headers=_headers).text, "lxml")
            block = bs(
                json.loads(
                    soup.find("script", string=re.compile(r'{"sitecore"'))
                    .text.replace("\\u002F", "/")
                    .replace("\\u003C\\u003Ch2\\u003E\\n", "</h2>")
                    .replace("\\u003Ch2\\u003E", "<h2>")
                    .replace("\\u003C\\u002Fp\\u003E\\n", "</p>")
                    .replace("\\u003Cp\\u003E", "<p>")
                    .replace("\\u003C\\u003Cstrong\\u003E\\n", "</strong>")
                    .replace("\\u003Cstrong\\u003E", "<strong>")
                )["sitecore"]["route"]["placeholders"]["article-section"][0]["fields"][
                    "body"
                ][
                    "value"
                ],
                "lxml",
            )
            location_name = raw_address = phone = ""
            if country == "Angola":
                for _ in block.select("p")[1:]:
                    bb = list(_.stripped_strings)
                    lat, lng = bb[-1].split("Details:")[-1].split(")")[0].split(",")
                    yield _d(country, base_url, bb[0], bb[1], bb[2], bb[4], lat, lng)

            elif country == "Namibia":
                location_name = block.strong.text.strip()
                raw_address = list(
                    block.find("", string=re.compile(r"^Address"))
                    .find_parent("p")
                    .stripped_strings
                )[-1].replace(":", "")
                if block.find("", string=re.compile(r"^Tel")):
                    phone = list(
                        block.find("", string=re.compile(r"^Tel"))
                        .find_parent("p")
                        .stripped_strings
                    )[-1].replace(":", "")
                yield _d(country, base_url, location_name, raw_address, phone)

            elif country == "Ecuador":
                location_name = " ".join(block.select("p")[1].stripped_strings)
                raw_address = list(
                    block.find("", string=re.compile(r"^Domicilio"))
                    .find_parent("p")
                    .stripped_strings
                )[-1].replace(":", "")
                if block.find("", string=re.compile(r"^Tel")):
                    phone = list(
                        block.find("", string=re.compile(r"^Tel"))
                        .find_parent("p")
                        .stripped_strings
                    )[-1].replace(":", "")
                yield _d(country, base_url, location_name, raw_address, phone)

            elif country == "Zambia":
                location_name = block.strong.text.strip()
                raw_address = list(
                    block.find("", string=re.compile(r"^Address"))
                    .find_parent("p")
                    .stripped_strings
                )[-1].replace(":", "")
                raw_address += " " + list(
                    block.find("", string=re.compile(r"^Postal Code"))
                    .find_parent("p")
                    .stripped_strings
                )[-1].replace(":", "")
                if block.find("", string=re.compile(r"^Tel")):
                    phone = list(
                        block.find("", string=re.compile(r"^Tel"))
                        .find_parent("p")
                        .stripped_strings
                    )[-1].replace(":", "")
                yield _d(country, base_url, location_name, raw_address, phone)

            elif country == "Zimbabwe":
                location_name = " ".join(block.select("p")[1].stripped_strings)
                raw_address = list(
                    block.find("", string=re.compile(r"^Address"))
                    .find_parent("p")
                    .stripped_strings
                )[-1].replace(":", "")
                if block.find("", string=re.compile(r"^Tel")):
                    phone = list(
                        block.find("", string=re.compile(r"^Tel"))
                        .find_parent("p")
                        .stripped_strings
                    )[-1].replace(":", "")
                yield _d(country, base_url, location_name, raw_address, phone)


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
