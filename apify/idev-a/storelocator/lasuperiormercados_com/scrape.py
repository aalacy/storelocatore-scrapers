from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl


locator_domain = "http://www.lasuperiormercados.com/"
base_url = "http://www.lasuperiormercados.com/locations.aspx#"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url).text, "lxml")
        stores = soup.select("div#subRightCol2 > div")
        for _ in stores[:-1]:
            block = list(_.stripped_strings)
            try:
                coord = _.a["href"].split("&ll=")[1].split("&")[0].split(",")
            except:
                try:
                    coord = (
                        _.a["href"].split("!2d")[1].split("!2m")[0].split("!3d")[::-1]
                    )
                except:
                    pass

            addr = parse_address_intl(" ".join(block[1:3]))
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=block[0],
                street_address=addr.street_address_1,
                city=addr.city,
                zip_postal=addr.postcode,
                state=addr.state,
                phone=block[3].split(":")[1].strip(),
                country_code="US",
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation=block[-2].replace("Hours:", ""),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
