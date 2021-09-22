from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.mcdonalds.at"
base_url = "https://www.mcdonalds.at/produkte/news/oeffnungszeiten#restaurants"


def _hr(temp):
    hours = []
    for hh in temp.split(","):
        if (
            "FT wie Wochentag" in hh
            or "Feiertag wie Wochentag" in hh
            or "FT geschlossen" in hh
        ):
            break
        hours.append(
            hh.split("Feiertag")[0].split("von")[0].split("(")[0].split("Mc")[0]
        )
    return hours


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.views-row-5 div.field--description ul li")
        for x, _ in enumerate(locations):
            if not _.text.replace("\xa0", "").strip() or _.b:
                continue
            addr = list(_.stripped_strings)
            raw_address = addr[0].replace("Pop up Store", "").replace("\t", " ").strip()
            if raw_address == "Restaurant & M":
                continue
            temp = ":".join(
                "".join(addr[1:]).replace("\xa0", " ").split(":")[1:]
            ).strip()
            hours = []
            if "Bis auf Weiteres" in "".join(addr[1:]):
                hours = ["Closed"]
            elif temp:
                hours = _hr(temp)

            if not hours:
                hours = _hr(
                    ":".join(
                        "".join(list(locations[x + 1].stripped_strings)).split(":")[1:]
                    ).strip()
                )
            _city = raw_address.split(",")[0].split(" ")
            yield SgRecord(
                page_url=base_url,
                street_address=" ".join(raw_address.split(",")[1:]).strip(),
                city=" ".join(_city[1:]),
                zip_postal=_city[0],
                country_code="Austria",
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.ZIP})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
