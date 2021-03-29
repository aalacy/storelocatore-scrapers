from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
import re
from sgscrape.sgpostal import parse_address_intl

locator_domain = "https://ladiperie.com/"
base_url = (
    "https://www.google.com/maps/d/u/4/embed?mid=1gVbpbLuD5Y9iwEIhrzNCxcJaikOXhmOu"
)


def _headers():
    return {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
        "Referer": "https://ladiperie.com/",
    }


def _phone(val):
    return val.replace("-", "").replace(")", "").replace("(", "").strip().isdigit()


def fetch_data():
    streets = []
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers())
        cleaned = (
            res.text.replace("//", "")
            .replace('\\"', '"')
            .replace("\\n]", "]")
            .replace("\\n,", ",")
            .replace("\\n", "#")
            .replace("\\", "")
        )
        block = re.search(
            r'\[\[\["\w+",\[\[\[\d+[.]\d+,[-]\d+[.]\d+\]\]\](.*)\]\],\[\[\["data:image',
            cleaned,
        )
        locations = json.loads(
            block.group().replace(
                ',[[["data:image',
                "",
            )[1:-1]
            + "]"
        )
        for _ in locations:
            location_name = _[5][0][1][0]
            sharp = _[5][1][1][0].split("#")
            hours = []
            for x, ss in enumerate(sharp):
                if _phone(ss):
                    phone = ss.replace(u"\xa0", " ").strip()
                    address = " ".join(sharp[:x])
                    for hh in sharp[x + 1 :]:
                        if not hh.replace(u"\xa0", " ").strip():
                            continue
                        hours.append(hh.replace(u"\xa0", " ").strip())
                    break
            addr = parse_address_intl(address)
            if addr.street_address_1 in streets:
                continue
            streets.append(addr.street_address_1)
            yield SgRecord(
                location_name=location_name,
                store_number=_[7],
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="CA",
                phone=phone,
                latitude=_[1][0][0][0],
                longitude=_[1][0][0][1],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
