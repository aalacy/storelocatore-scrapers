from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _valid(val):
    return (
        val.replace("–", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa0\\xa", " ")
        .replace("\\xa0", " ")
        .replace("\\xae", " ")
        .replace("\\u2022", " ")
    )


locator_domain = "https://www.poundstretcher.co.uk/"
base_url = "https://www.poundstretcher.co.uk/find-a-store"


def _p(val):
    if (
        val
        and val.replace("(", "")
        .encode("unicode-escape")
        .decode("utf8")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .replace("\\xa0", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        scripts = [
            script.contents[0] for script in soup.find_all("script") if script.contents
        ]
        items = []
        for script in scripts:
            if "initial_locations:" in script:
                items = json.loads(
                    script.split("initial_locations:")[1]
                    .strip()
                    .split("min_zoom: 10,")[0]
                    .strip()[:-1]
                )
                break

        for item in items:
            page_url = locator_domain + item["website_url"]
            logger.info(page_url)
            location_name = item["title"].strip()
            raw_address = (
                item["address_display"]
                .replace("\n", "")
                .replace("\r", " ")
                .replace("UK", "")
                .strip()
            )
            soup2 = bs(item["notes"], "lxml")
            hours = []
            for _ in soup2.select("tr"):
                if not _.td:
                    continue
                hours.append(f"{_.th.text.strip()} {_.td.text.strip()}")

            addr = parse_address_intl(raw_address + ", United Kingdom")
            street_address = addr.street_address_1 or ""
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            zip_postal = addr.postcode
            state = ""
            city = addr.city
            if not city:
                city = location_name

            location_type = "<MISSING>"
            phone = item.get("phone")
            res = session.get(page_url, headers=_headers)
            if res.status_code == 200 and res.url.__str__() != base_url:
                soup1 = bs(res.text, "html.parser")
                if soup1.select("div#store-address"):
                    _address = list(
                        soup1.select("div#store-address")[-1].stripped_strings
                    )

                    if _address[0] == "Address & Contact Details":
                        _address = _address[1:]
                        location_type = _address[0]

                    if len(_address) < 3:
                        _address = _address + list(
                            soup1.select("div#store-address")[-1]
                            .find_next_sibling()
                            .stripped_strings
                        )

                    if _p(_address[-1].replace("Tel:", "")):
                        if not phone:
                            phone = _address[-1]
                        _address = _address[:-1]

                    if "Tel:" in _address[-1]:
                        del _address[-1]

                    if _address[-1] == "UK":
                        _address.pop()

                    raw_address = (
                        ", ".join(_address[1:]).replace("\n", "").replace("\r", " ")
                    )
                    zip_postal = _address[-1]
                    city = _address[-2]
                    st_idx = -2
                    if city == "Northern Ireland":
                        state = "Northern Ireland"
                        city = _address[-3]
                        st_idx -= -1
                    street_address = ", ".join(_address[1:st_idx])

                    if city in [
                        "The Orchards Shopping Centre",
                        "44-52 Broadwalk North",
                        "Strabane Retail Park",
                    ]:
                        street_address += ", " + city
                        city = location_name.replace("Bargain Buys", "").strip()

            yield SgRecord(
                page_url=page_url,
                store_number=item["location_id"],
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                phone=phone,
                latitude=item["latitude"],
                longitude=item["longitude"],
                location_type=location_type,
                country_code=item["country"],
                locator_domain=locator_domain,
                hours_of_operation=_valid("; ".join(hours)),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
