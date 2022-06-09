from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://aldoshoes.com.cy"
base_url = "https://aldoshoes.com.cy/en/stores"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.weasy_page_content div.omw-sentence")
        for _ in locations:
            if not _.p or not _.text.strip():
                continue
            block = []
            for bb in _.select("p")[:-1]:
                block += list(bb.stripped_strings)
            raw_address = " ".join(block[1:]).split("|")[0]
            addr = parse_address_intl(raw_address + ", Cyprus")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            zip_postal = addr.postcode
            if not city:
                c_z = block[-1].split("|")[0].split()
                if c_z[0].strip().isdigit():
                    city = c_z[-1]
                    zip_postal = c_z[0]
                else:
                    city = c_z[0]
                    zip_postal = c_z[1]
            if street_address.isdigit():
                street_address = block[2]
            if street_address.split()[-1].lower() == city.lower():
                street_address = " ".join(street_address.split()[:-1])
            yield SgRecord(
                page_url=base_url,
                location_name=block[0],
                street_address=street_address,
                city=block[0].lower(),
                zip_postal=zip_postal,
                country_code="Cyprus",
                locator_domain=locator_domain,
                hours_of_operation="; ".join(_.select("p")[-1].stripped_strings),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
