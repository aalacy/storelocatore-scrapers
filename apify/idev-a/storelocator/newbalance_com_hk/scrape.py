from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re
from sgpostal.sgpostal import parse_address_intl


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://newbalance.com.hk/"
hk_url = "https://www.newbalance.com.hk/zh/stores/#"
sg_url = "https://www.newbalance.com.sg/stores/#"
tw_url = "https://www.newbalance.com.tw/stores/#"


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


def _name(_):
    name = ""
    for nn in (
        _.find_parent()
        .find_parent()
        .find_parent()
        .find_parent()
        .find_previous_siblings()
    ):
        if not nn.text.strip():
            continue
        if "experience-commerce_assets-centerAlignedTextImage" not in nn["class"]:
            continue
        name = nn.select_one("div.bold").text.strip()
        break

    return "New Balance " + name


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(hk_url, headers=_headers).text, "lxml")
        locations = soup.select("div.container div.card")
        for _ in locations:
            if not _.text.strip():
                continue

            name = _name(_)
            if "Authorized Retailers" in name:
                continue
            raw_address = _.p.text.strip()
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            country_code = "HK"
            city = addr.city
            state = addr.state
            if "澳門" in raw_address:
                country_code = "Macao"
                state = ""
                city = "澳門"
                street_address = raw_address.replace("澳門", "")
            if street_address == "2 樓":
                street_address = raw_address
            try:
                latitude, longitude, temp = (
                    _.select("a")[-1]["href"].split("/@")[1].split("/")[0].split(",")
                )
            except:
                latitude = longitude = ""

            yield SgRecord(
                page_url=hk_url,
                location_name=name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=addr.postcode,
                country_code=country_code,
                phone=_p(_.a.text.strip()),
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                raw_address=raw_address,
            )

        soup = bs(session.get(sg_url, headers=_headers).text, "lxml")
        locations = soup.select("div.container div.card")
        for _ in locations:
            if not _.text.strip():
                continue

            name = _name(_)
            if "Authorized Retailers" in name:
                continue

            blocks = list(_.select_one("div.col-12").stripped_strings)[1:]
            addr = []
            phone = ""
            hours = []
            for x, bb in enumerate(blocks):
                if "Tel" in bb:
                    addr = blocks[:x]
                    phone = blocks[x + 1]
                if "Opening" in bb:
                    if not addr:
                        addr = blocks[:x]
                    hours = blocks[x + 1 :]

            try:
                latitude, longitude, temp = (
                    _.select("a")[-1]["href"].split("/@")[1].split("/")[0].split(",")
                )
            except:
                latitude = longitude = ""

            yield SgRecord(
                page_url=sg_url,
                location_name=name,
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split()[0],
                zip_postal=addr[-1].split()[-1],
                country_code="SG",
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=" ".join(addr),
            )

        soup = bs(session.get(tw_url, headers=_headers).text, "lxml")
        locations = soup.select("div.container div.card")
        for _ in locations:
            if not _.text.strip():
                continue

            name = _name(_)

            blocks = list(_.select_one("div.col-12").stripped_strings)[1:]
            addr = []
            phone = ""
            hours = ""
            _pp = _.find("", string=re.compile(r"電話"))
            if _pp:
                phone = "".join(list(_pp.find_parent("p").stripped_strings)[1:])
            for x, bb in enumerate(blocks):
                if "電話" in bb:
                    addr = blocks[:x]

                if "營業時間" in bb:
                    if not addr:
                        addr = blocks[:x]
                    hours = bb.replace("營業時間:", "").strip()
            try:
                latitude, longitude, temp = (
                    _.select("a")[-1]["href"].split("/@")[1].split("/")[0].split(",")
                )
            except:
                latitude = longitude = ""

            city = addr[0].split("市")[0] + "市"
            yield SgRecord(
                page_url=tw_url,
                location_name=name,
                street_address=addr[0].split("市")[-1].split("區")[-1],
                city=city,
                country_code="TW",
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours,
                raw_address=addr[0],
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
