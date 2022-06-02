from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re
from sgpostal.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.acehardware.mv"
base_url = "https://www.acehardware.mv/contact-us/"


def _coord(locs, name):
    coord = ["", ""]
    for loc in locs:
        if loc.text.strip() in name:
            coord = loc["href"].split("@")[1].split("/data")[0].split(",")
            break
    return coord


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locs = soup.find_all("a", href=re.compile(r"www.google.com/maps/place/"))
        locations = soup.select("div.vc_column_container.vc_col-sm-4")
        for _ in locations:
            if not _.text.strip() or not _.strong:
                continue
            location_name = _.strong.text.strip()
            coord = _coord(locs, location_name)
            raw_address = " ".join(
                _.select_one("div.wpb_text_column p").stripped_strings
            )
            raw_address = " ".join([rr for rr in raw_address.split() if rr.strip()])
            phone = (
                list(_.select("div.wpb_text_column p")[1].stripped_strings)[0]
                .split(":")[-1]
                .strip()
            )
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            _hr = _.find("strong", string=re.compile(r"Shop Opening Hours"))
            hoo = {}
            temp = []
            hours = []
            if _hr:
                for ho in _hr.find_parent().find_next_siblings("div"):
                    temp += list(ho.stripped_strings)
            for hh in temp:
                day1 = hh.replace("\xa0", " ").split("  ")[0].strip()
                day2 = hh.replace("\xa0", " ").split("  ")[-1].strip()
                if not hoo:
                    hoo[day1] = []
                    hoo[day2] = []
                else:
                    hoo[list(hoo.keys())[0]].append(day1)
                    hoo[list(hoo.keys())[1]].append(day2)

            for day, times in hoo.items():
                hours.append(f"{day}: {', '.join(times)}")

            yield SgRecord(
                page_url=base_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="Republic of Maldives",
                phone=phone.replace("P", "").strip(),
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                raw_address=raw_address,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
