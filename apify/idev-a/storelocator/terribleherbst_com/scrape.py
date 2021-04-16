from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
import re

locator_domain = "https://www.terribleherbst.com/"
base_url = "https://www.google.com/maps/d/u/0/embed?mid=17KgQXKUbt-foi_HwjRewevjQtKwwkz1d&ll=36.19329398425036%2C-115.17575742154983&z=13"


def _headers():
    return {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
        "Referer": "https://www.terribleherbst.com/",
    }


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers())
        cleaned = res.text.replace("\\n", "").replace("\\", "").replace("//", "")
        block = re.search(
            r'\[\[\["\w+",\[\[\[\d+[.]\d+,[-]\d+[.]\d+\]\]\](.*)\]\],\[\[\["data:image\/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIAAAABaCAYAAABwm16CAAAaC0lEQVR42u1dB3hVVbbWGccZdd6b',
            cleaned,
        )
        locations = json.loads(
            block.group().replace(
                ',[[["data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIAAAABaCAYAAABwm16CAAAaC0lEQVR42u1dB3hVVbbWGccZdd6b',
                "",
            )
            + "]"
        )[0]
        for _ in locations:
            store_number = _[5][0][1][0]
            location_name = f"Terrible's - {store_number}"
            street_address = _[5][3][0][1][0]
            city_state = _[5][3][1][1][0]
            zip_postal = _[5][3][2][1][0]
            phone = "<MISSING>"
            try:
                if _[5][3][3][0] == "TELEPHONE #":
                    phone = _[5][3][3][1][0]
            except:
                pass
            if phone.strip() == "CAR WASH":
                import pdb

                pdb.set_trace()
            state = "<MISSING>"
            try:
                state = city_state.split(",")[1].strip()
            except:
                pass
            _dir = _[1][0][0]
            record = SgRecord(
                location_name=location_name,
                store_number=store_number,
                street_address=street_address,
                city=city_state.split(",")[0].strip(),
                state=state,
                zip_postal=zip_postal,
                country_code="US",
                phone=phone,
                latitude=_dir[0],
                longitude=_dir[1],
                locator_domain=locator_domain,
            )
            yield record


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
