from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from sgscrape.sgpostal import parse_address_intl

locator_domain = "http://www.winotstop.com/"
base_url = "https://www.google.com/maps/d/u/0/embed?mid=1bhjoPX9KjTp7NSJTRRGwoOPUYmA"
map_url = "https://www.google.com/maps/dir//38.8619831,-77.8480371/@{},{}z"


def _headers():
    return {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
        "Referer": "https://ladiperie.com/",
    }


def _phone(val):
    return (
        val.replace("Phone", "")
        .replace("-", "")
        .replace(")", "")
        .replace("(", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    streets = []
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers())
        cleaned = (
            res.text.replace("\\t", " ")
            .replace("\t", " ")
            .replace("\\n]", "]")
            .replace("\n]", "]")
            .replace("\\n,", ",")
            .replace("\\n", "#")
            .replace('\\"', '"')
            .replace("\\u003d", "=")
            .replace("\\u0026", "&")
            .replace("\\", "")
            .replace("\xa0", " ")
        )
        locations = json.loads(
            cleaned.split('var _pageData = "')[1].split('";</script>')[0][:-1]
        )
        open("w", "w").write(
            cleaned.split('var _pageData = "')[1].split('";</script>')[0][:-1]
        )
        for _ in locations[1][6][0][12][0][13][0]:
            location_name = _[5][0][1][0]
            sharp = [
                ss.strip()
                for ss in _[5][1][1][0].replace("  ", "#").split("#")
                if ss.strip()
            ]
            phone = ""
            for ss in sharp:
                if _phone(ss):
                    phone = ss.replace("Phone", "")
                    break
            latitude = _[1][0][0][0]
            longitude = _[1][0][0][1]
            res = session.get(
                map_url.format(latitude, longitude), headers=_headers
            ).text
            cleaned_res = (
                res.replace("\n,[", ",[")
                .replace("\n],", "],")
                .replace("\n]", "]")
                .replace("\\u003d", "=")
                .replace("\\u0026", "&")
                .replace("\\u003e", ">")
                .replace("\\u003c", "<")
                .replace("\\\\", "")
                .replace("\\n", "")
                .replace("\n", "")
                .replace("\n", "")
            )
            addr = parse_address_intl(cleaned_res)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2
            if street_address in streets:
                continue
            streets.append(street_address)
            city = addr.city
            state = addr.state
            yield SgRecord(
                location_name=location_name,
                store_number=_[7],
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=addr.postcode,
                country_code="CA",
                phone=phone,
                latitude=latitude,
                longitude=latitude,
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
