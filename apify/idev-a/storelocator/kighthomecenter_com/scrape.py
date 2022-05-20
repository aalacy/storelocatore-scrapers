from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.kighthomecenter.com"
base_url = "https://www.kighthomecenter.com/locations/"


def _p(val):
    if (
        val
        and val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        tables = soup.select("div.std table")
        for table in tables:
            location_type = (
                table.find_previous_sibling("h2").text.replace("Locations", "").strip()
            )
            locations = table.select("td")
            for _ in locations:
                if not _.h3:
                    continue
                addr = list(_.p.stripped_strings)
                phone = ""
                if _p(addr[-1]):
                    phone = addr[-1]
                    del addr[-1]

                if "Phone" in addr[-1]:
                    del addr[-1]

                hours = []
                temp = list(_.select("p")[1].stripped_strings)
                for x in range(0, len(temp), 2):
                    hours.append(f"{temp[x]} {temp[x+1]}")

                yield SgRecord(
                    page_url=base_url,
                    location_name=_.h3.text.strip(),
                    street_address=" ".join(addr[:-1])
                    .replace("Kitchen Interiors", "")
                    .replace("Kight Kitchen & Design Center", "")
                    .strip(),
                    city=addr[-1].split(",")[0].strip(),
                    state=addr[-1].split(",")[1].strip().split()[0].strip(),
                    zip_postal=addr[-1].split(",")[1].strip().split()[-1].strip(),
                    country_code="US",
                    phone=phone,
                    location_type=location_type,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    raw_address=" ".join(addr),
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
