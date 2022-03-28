from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("absolute")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.absolute-run.eu"
base_url = "https://www.absolute-run.eu/"


def _d(page_url, location_name, addr, phone, hours):
    return SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=addr[0],
        city=addr[1].split()[-1],
        zip_postal=addr[1].split()[0],
        country_code="DE",
        phone=phone.replace("Tel", "").replace(".", "").strip(),
        locator_domain=locator_domain,
        raw_address=" ".join(addr),
        hours_of_operation="; ".join(hours),
    )


def _ad(ch):
    td = ch.select("td")
    addr = [td[0].text.strip()] + [td[2].text.strip()]
    phone = td[1].text

    return addr, phone


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.teaser-item a")
        urls = []
        for _ in locations:
            page_url = _["href"]
            if page_url in urls or page_url == "https://www.absolute-teamsport.eu/":
                continue
            urls.append(page_url)
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")

            if "please wait" in sp1.text:
                continue

            hours = []
            location_name = phone = ""
            addr = []
            is_done = False

            if sp1.select("div#text-2 div.textwidget p"):
                location_name = sp1.select_one("div#text-2 h2").text.strip()
                addr = list(
                    sp1.select("div#text-2 div.textwidget p")[1].stripped_strings
                )
                if "tel" in sp1.select("div#text-2 div.textwidget p")[2].text:
                    phone = list(sp1.select("div#text-2 div.textwidget p")[2])[0].split(
                        ":"
                    )[-1]
                hours = [
                    ": ".join(tr.stripped_strings)
                    for tr in sp1.select("table.op-table tr")[1:]
                ]
            elif sp1.select("footer div.textwidget"):
                addr = list(sp1.select_one("footer div.textwidget p").stripped_strings)[
                    1:
                ]
                if "Tel" in sp1.select("footer div.textwidget p")[1].text:
                    phone = sp1.select("footer div.textwidget p")[1].a.text
                hours = sp1.select("footer div.textwidget")[1].p.stripped_strings
            elif sp1.select_one(
                "div.mod_article div.container div.row div.ce_text.first.col-lg-6"
            ):
                for ch in sp1.select_one(
                    "div.mod_article div.container div.row div.ce_text.first.col-lg-6"
                ).findChildren(recursive=False):
                    if not ch.text.strip():
                        continue
                    if "Öffnungszeiten" not in ch.text:
                        if ch.name == "h2":
                            location_name = ch.text.strip()
                        elif (
                            ch.h2
                            and "Öffnungszeiten" != ch.select("h2")[-1].text.strip()
                        ):
                            location_name = ch.select("h2")[-1].text.strip()

                        if ch.table:
                            addr, phone = _ad(ch.table)

                    if not addr and ch.name == "table":
                        addr, phone = _ad(ch)

                    if ch.h2 and "Öffnungszeiten" in ch.h2.text:
                        hours = [
                            ": ".join(hh.stripped_strings)
                            for hh in ch.table.select("tr")
                        ]
                    if (
                        ch.name == "h2"
                        and "Öffnungszeiten" in ch.text
                        and ch.find_next_sibling().name == "table"
                    ):
                        hours = [
                            ": ".join(hh.stripped_strings)
                            for hh in ch.find_next_sibling().select("tr")
                        ]

                    if location_name and addr and hours:
                        yield _d(page_url, location_name, addr, phone, hours)

                        phone = location_name = ""
                        hours = []

                is_done = True
            elif sp1.select("div.last-paragraph-no-margin"):
                addr = list(
                    sp1.select("div.last-paragraph-no-margin p")[1].stripped_strings
                )
                if "Tel" in sp1.select("div.last-paragraph-no-margin p")[2].text:
                    phone = sp1.select("div.last-paragraph-no-margin p")[2].text
                hours = (
                    sp1.select("div.last-paragraph-no-margin")[1]
                    .select("p")[1]
                    .stripped_strings
                )
            elif sp1.select("div.xr_txt.Logo_Big"):
                block = list(sp1.select("div.xr_txt.Logo_Big")[1].stripped_strings)
                if "@" in block[-1]:
                    del block[-1]
                if "Phone" in block[-1]:
                    phone = block[-1].replace("Phone", "").replace(":", "")
                    del block[-1]

            if not is_done:
                location_name = " ".join(
                    _.select_one("div.teaser-item-content").stripped_strings
                )
                yield _d(page_url, location_name, addr, phone, hours)


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
