from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("visiblescm")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.maersk.com"
base_url = "https://www.maersk.com/api_sc9/local-info/offices"


def fetch_data():
    with SgRequests() as session:
        regions = session.get(base_url, headers=_headers).json()["data"]
        for region in regions:
            region_url = locator_domain + region["lookupUrl"]
            logger.info(region_url)
            locations = bs(
                session.get(region_url, headers=_headers).text, "lxml"
            ).select("div.p-section__find-an-office__detail")
            for _ in locations:
                title = list(
                    _.select_one(
                        "div.p-section__find-an-office__detail__title"
                    ).stripped_strings
                )
                raw_address = list(
                    _.select_one(
                        "div.p-section__find-an-office__detail__address"
                    ).stripped_strings
                )[-1].replace("blast',", "blast,")
                addr = parse_address_intl(raw_address)
                street_address = addr.street_address_1 or ""
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                phones = list(
                    _.select_one(
                        "div.p-section__find-an-office__detail__tel"
                    ).stripped_strings
                )
                if len(phones) > 1:
                    phone = phones[1]
                    if phone.endswith(":"):
                        phone = phones[2]
                    phone = (
                        phone.replace("Tél", "")
                        .replace("Tel", "")
                        .split(":")[-1]
                        .split(",")[0]
                        .split("ext")[0]
                        .split("/")[0]
                        .split("Logistics)")[-1]
                        .split("( within")[0]
                        .split(";")[0]
                        .split("within")[0]
                        .replace("#1", "")
                        .replace("Customer Service", "")
                        .replace("Local Calls", "")
                        .replace("(Reception Desk)", "")
                        .strip()
                    )
                    if phone.endswith("-"):
                        phone = phone[:-1]
                    if "スにお問合わせください" in phone or "@" in phone:
                        phone = ""
                hours = []
                try:
                    for hh in list(
                        _.select_one(
                            "div.p-section__find-an-office__detail__hours"
                        ).stripped_strings
                    )[1:]:
                        if hours and (
                            "Counter" in hh
                            or "Deliver" in hh
                            or "Duty" in hh
                            or "when" in hh
                            or "Call Center" in hh
                        ):
                            break
                        if hh == "Counter":
                            continue
                        if hh.startswith("(") or "activity" in hh:
                            continue
                        hr = (
                            hh.split("Hours:")[-1]
                            .split("HOURS")[-1]
                            .split("Office")[-1]
                            .split("CUSTOMER")[0]
                            .split("Counter")[0]
                            .split("ouverture:")[-1]
                            .split("For")[0]
                            .replace("|", ";")
                            .replace("Gezairi", "")
                            .strip()
                        )
                        if hr.startswith(":"):
                            hr = hr[1:]
                        if hr.endswith(",") or hr.endswith("|"):
                            hr = hr[:-1]
                        hours.append(hr.replace("hSamedi", "h; Samedi"))
                except:
                    hours = []
                coord = ["", ""]
                try:
                    ll = _.select_one(
                        "div.p-section__find-an-office__detail__controls a"
                    )
                    if ll and "Get directions" in ll.text:
                        if "place/" in ll["href"]:
                            coord = (
                                ll["href"].split("place/")[-1].split('"')[0].split(",")
                            )
                        elif "/@" in ll["href"]:
                            coord = ll["href"].split("/@")[-1].split('"')[0].split(",")
                        if len(coord) == 1:
                            coord = coord[0].split()
                except:
                    coord = ["", ""]

                city = addr.city
                if not city:
                    city = title[1].split("–")[-1].strip()
                country_code = addr.country
                if not country_code:
                    country_code = region_url.split("/")[-1]
                yield SgRecord(
                    page_url=region_url,
                    location_name=title[1],
                    street_address=street_address,
                    city=city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code=country_code,
                    phone=phone,
                    location_type=title[0],
                    latitude=coord[0],
                    longitude=coord[1],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours)
                    .replace(":;", ":")
                    .replace("hVen:", "h; Ven:"),
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
