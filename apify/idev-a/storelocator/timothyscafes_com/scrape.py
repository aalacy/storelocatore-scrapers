from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://timothyscafes.com"
base_url = "https://timothyscafes.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=en&t=1625939044230"
page_url = "https://timothyscafes.com/locations/"


def fetch_data():
    with SgRequests() as session:
        locations = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "locator store item"
        )
        for _ in locations:
            addr = parse_address_intl(_.address.text)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            location_name = _.location.text.replace("&#44;", ",").replace("&#39;", "'")
            location_type = ""
            if "TEMPORARILY CLOSED" in location_name:
                location_type = "TEMPORARILY CLOSED"
            if "(CLOSED)" in location_name:
                location_type = "CLOSED"
            hours = []
            if _.operatinghours:
                temp = list(
                    bs(
                        _.operatinghours.text.replace("&amp;", "&"), "lxml"
                    ).stripped_strings
                )
                for hh in "; ".join(temp).split(";"):
                    if not hh.strip() or "Hours" in hh:
                        continue
                    if "Good" in hh:
                        break
                    hours.append(hh)
            yield SgRecord(
                page_url=page_url,
                store_number=_.storeId.text if _.storeId else _.storeid.text,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_.latitude.text,
                longitude=_.longitude.text,
                country_code="CA",
                phone=_.telephone.text,
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=_.address.text.replace("&#44;", ","),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
