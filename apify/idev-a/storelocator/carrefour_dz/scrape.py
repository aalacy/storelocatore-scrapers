from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.carrefour.dz"
base_url = "https://www.carrefour.dz/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.site-footer-locations p")
        location_name = addr = ""
        locs = []
        for x, _ in enumerate(locations):
            if _.text.strip():
                if addr and not location_name:
                    location_name = _.text.strip()
                if not addr:
                    addr = _.text.strip()

            if (
                location_name
                and addr
                and (not _.text.strip() or x == len(locations) - 1)
            ):
                locs.append(dict(location_name=location_name, addr=addr))
                location_name = addr = ""

        hours = []
        hh = []
        hr = soup.select("div.site-footer-operating-hours p")
        idx = 0
        for x, _ in enumerate(hr):
            if _.text.strip() and idx % 3 > 0:
                hh.append(_.text.strip())

            idx += 1
            if (not _.text.strip() or x == len(locations) - 1) and hh:
                hours.append(hh)
                hh = []
                idx = 0

        for x, _ in enumerate(locs):

            yield SgRecord(
                page_url=base_url,
                location_name=_["location_name"],
                street_address=_["addr"],
                city=_["location_name"],
                country_code="Algeria",
                locator_domain=locator_domain,
                location_type="Carrefour",
                hours_of_operation="; ".join(hours[x]),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.CITY})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
