from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://www.gloriajeanscoffees.my"
base_url = "http://www.gloriajeanscoffees.my/our-store"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select(
            "div.uk-section-default > div > div.uk-container div.tm-grid-expand"
        )
        for _ in locations:
            if not _.h2:
                continue
            raw_address = " ".join(_.p.stripped_strings)
            addr = raw_address.split(",")
            if "Wilayah Persekutuan" in addr[-1]:
                del addr[-1]
            if "Malaysia" in addr[-1]:
                del addr[-1]
            c_z = addr[-1].split()
            s_idx = -1
            if c_z[0].isdigit():
                city = " ".join(c_z[1:])
                zip_postal = c_z[0]
            else:
                s_idx -= 1
                city = " ".join(c_z)
                zip_postal = addr[-2].split()[0]
            if city == "Wilayah Persekutuan" and "Kuala Lumpur" in raw_address:
                city = "Kuala Lumpur"
            street_address = ", ".join(addr[:s_idx])
            hours = [": ".join(hh.stripped_strings) for hh in _.select("ul.uk-list li")]
            ss = json.loads(_.find("script", type="application/json").string)[
                "markers"
            ][0]
            yield SgRecord(
                page_url=base_url,
                location_name=_.h2.text.strip(),
                street_address=street_address,
                city=city,
                zip_postal=zip_postal,
                country_code="MY",
                latitude=ss["lat"],
                longitude=ss["lng"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
