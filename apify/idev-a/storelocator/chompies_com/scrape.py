from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("chompies")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://chompies.com"
base_url = "https://chompies.com/contact/"
json_url = "https://chompies.com/wp-json/wpgmza/v1/features/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMoxRqlWqBQCnUQoG"


def _coord(locations, address):
    for loc in locations:
        if (
            " ".join(loc["address"].split(",")[0].replace(".", "").split()[:2])
            in address
        ):
            return loc


def fetch_data():
    with SgRequests() as session:
        locs = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "div.so-panel.widget"
        )
        locations = session.get(json_url, headers=_headers).json()["markers"]
        for loc in locs:
            if not (loc.h4 and loc.h4.a):
                continue
            page_url = locator_domain + loc.h4.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            blocks = list(
                sp1.select_one(
                    "div.siteorigin-widget-tinymce.textwidget"
                ).stripped_strings
            )[1:]
            raw_address = ""
            phone = ""
            hours = []

            hr = []
            temp = []
            for x, bb in enumerate(blocks):
                if "Phone:" in bb:
                    raw_address = blocks[x - 1]
                    phone = blocks[x + 1]
                    hr = blocks[x + 2 :]
                    break
            for hh in hr:
                if "7 days" in hh:
                    continue
                if "Chompie" in hh:
                    break
                temp.append(hh)

            if len(temp) % 2 == 0 and "Mon" not in temp[0]:
                for x in range(0, len(temp), 2):
                    hours.append(f"{temp[x]}: {temp[x+1]}")
            else:
                hours = temp

            addr = raw_address.split(",")
            info = _coord(locations, raw_address)
            yield SgRecord(
                page_url=page_url,
                store_number=info["id"],
                location_name=loc.h4.text.strip(),
                street_address=", ".join(addr[:-2]),
                city=addr[-2],
                state=addr[-1].strip().split()[0].replace(".", ""),
                zip_postal=addr[-1].strip().split()[-1],
                latitude=info["lat"],
                longitude=info["lng"],
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
