from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetch_data():
    locator_domain = "https://www.arenewedmindservices.org"
    base_url = "https://www.arenewedmindservices.org/locationsandservices"
    with SgRequests() as session:
        blocks = (
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .select('main div[data-testid="mesh-container-content"]')[0]
            .select(
                'div[data-testid="mesh-container-content"] > div[data-testid="richTextElement"]'
            )
        )
        for block in blocks:
            if "Call for Application" in block.text or (
                "Phone" in block.text
                and ("Monday" in block.text or "Wednesday" in block.text)
            ):
                data = [dd.text.strip() for dd in block.select("p")]
                phone = ""
                location_name = data[0]
                for x, pp in enumerate(data):
                    if "Call for Application" in pp:
                        phone = (
                            pp.split(",")[0]
                            .split(":")[-1]
                            .replace("Call for Application", "")
                            .strip()
                        )
                        break
                    elif pp.startswith("Phone"):
                        phone = (
                            pp.split(",")[0]
                            .split("\xa0")[0]
                            .split(":")[-1]
                            .replace("Phone", "")
                            .strip()
                        )
                        break
                _addr = data[x - 1]
                if x == 1:
                    location_name = list(block.p.stripped_strings)[0]
                    _addr = " ".join(list(block.p.stripped_strings)[1:])
                else:
                    _addr = data[1]
                if location_name.endswith(":"):
                    location_name = location_name[:-1]
                addr = parse_address_intl(_addr)
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                hours = []
                if len(data) > 3:
                    temp = data[x + 1 :]
                    for hh in temp:
                        if (
                            hh == "\u200b"
                            or "Assessments" in hh
                            or "Psychiatry Services" in hh
                        ):
                            break
                        hh = hh.replace("\u200b", "")
                        if hh.split(" ")[0].split("-")[0] in days:
                            hours.append(hh)
                yield SgRecord(
                    page_url=base_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code="US",
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours).replace("–", "-"),
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
