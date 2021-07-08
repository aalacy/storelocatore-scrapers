from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json

locator_domain = "https://versacold.com"
base_url = (
    "https://mapsengine.google.com/map/embed?mid=1YiZzqHf00GMmToDfUa4ODmrZPUt68iVO"
)


def _headers():
    return {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
        "Referer": "https://ladiperie.com/",
    }


def _phone(val):
    return (
        val.split(":")[-1]
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
        )[1][6][1][12][0][13][0]
        for _ in locations:
            phone = ""
            hours = []
            try:
                idx = 1
                if _[5][3][idx][0] == "Phone":
                    phone = _[5][3][idx][1][0]
                    idx += 1
                for hh in _[5][3][idx:]:
                    if hh[1][0] == "N/A":
                        continue
                    hours.append(f"{hh[0]}: {hh[1][0]}")
            except:
                pass
            addr = _[5][3][0][1][0]
            if addr.endswith("#"):
                addr = addr[:-1]
            if len(addr.split(",")) == 3:
                street_address = addr.split(",")[0].strip()
                city = addr.split(",")[1].replace("#", "").strip()
            else:
                street_address = addr.split(",")[0].split("#")[0].strip()
                city = addr.split(",")[0].split("#")[1].strip()
            if street_address in streets:
                continue
            streets.append(street_address)
            state = addr.split(",")[-1].strip().split(" ")[0].split("#")[0].strip()
            zip_postal = (
                addr.split(",")[-1].strip().split("#")[-1].split(state)[-1].strip()
            )
            yield SgRecord(
                location_name=_[5][0][1][0],
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
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
