from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.pfchangs.com.co"
base_url = "https://www.pfchangs.com.co/ubicacion/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div#content div.vc_col-sm-6")
        for _ in locations:
            p = _.select("p")
            hours = []
            if "Formato" in p[0].text:
                raw_address = " ".join(p[1].stripped_strings)
                if p[2].span:
                    hours = p[2].span.stripped_strings
                else:
                    hours = p[2].stripped_strings
            else:
                raw_address = " ".join(p[0].stripped_strings)
                if p[1].span:
                    hours = p[1].span.stripped_strings
                else:
                    hours = p[1].stripped_strings
            if raw_address.startswith("-"):
                raw_address = raw_address[1:]
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            coord = _.iframe["src"].split("!2d")[1].split("!2m")[0].split("!3d")
            yield SgRecord(
                page_url=base_url,
                location_name=_.h2.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="Columbia",
                phone=list(p[-1].stripped_strings)[-1].split(":")[-1],
                latitude=coord[1],
                longitude=coord[0],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("– Horario :", ""),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
