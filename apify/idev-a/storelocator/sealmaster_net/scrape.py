from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _phone(val):
    return (
        val.replace("SEAL", "")
        .replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    locator_domain = "https://sealmaster.net"
    base_url = "https://sealmaster.net/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select(
            "div#av_section_2 div.entry-content-wrapper section.av_textblock_section"
        )
        for _ in locations:
            page_url = base_url
            if _.select("h4 a"):
                page_url = locator_domain + _.select("h4 a")[-1]["href"]
            if not _.p:
                continue
            addr = list(_.p.stripped_strings)
            if addr[-1] == "MAP":
                del addr[-1]
            phone = ""
            street_address = city = state = zip_postal = ""
            if len(addr) > 1:
                if "km" in addr[1]:
                    del addr[1]
                if _phone(addr[-1]):
                    phone = addr[-1]
                    del addr[-1]
                if _phone(addr[-1]):
                    phone = addr[-1]
                    del addr[-1]
                try:
                    street_address = " ".join(addr[:-1])
                    city = " ".join(addr[-1].split(" ")[-2])
                    state = addr[-1].split(" ")[-2].strip()
                    zip_postal = addr[-1].split(" ")[-1]
                except:
                    import pdb

                    pdb.set_trace()
            else:
                phone = addr[0]
            coord = ["", ""]
            if _.p.a:
                try:
                    coord = _.p.a["href"].split("/@")[1].split("z/data")[0].split(",")
                except:
                    pass
            yield SgRecord(
                page_url=page_url,
                location_name=_.select("h4")[-1].text,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                latitude=coord[0],
                longitude=coord[1],
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
