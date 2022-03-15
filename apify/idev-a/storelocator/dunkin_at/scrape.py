from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs
from lxml import etree

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://dunkin.at"
base_url = "https://dunkin.at/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=&t=1626103265505_)"


def fetch_data():
    with SgRequests() as session:
        locations = etree.HTML(session.get(base_url, headers=_headers).text).xpath(
            "//store/item"
        )
        for _ in locations:
            addr = parse_address_intl(_.xpath("./address/text()")[0])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            try:
                phone = ""
                if _.xpath("./telephone/text()"):
                    phone = _.xpath("./telephone/text()")[0]
                hours = list(bs(_.xpath(".//text()")[5], "lxml").stripped_strings)
                if "*" in hours[0]:
                    del hours[0]
                yield SgRecord(
                    page_url=base_url,
                    store_number=_.xpath("./storeId/text()")[0]
                    if _.xpath("./storeId")
                    else _.xpath("./storeid/text()")[0],
                    location_name=_.xpath("./location/text()")[0],
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    latitude=_.xpath("./latitude/text()")[0],
                    longitude=_.xpath("./longitude/text()")[0],
                    country_code="Austria",
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours).replace("–", "-").split("(")[0],
                )
            except:
                import pdb

                pdb.set_trace()


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
