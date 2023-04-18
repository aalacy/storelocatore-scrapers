from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl

locator_domain = "https://order.rolypoly.com/"
base_url = "https://order.rolypoly.com/api/v2/merchants/5be8b5d8-e45f-4f63-9063-51c0f89dfec5/place-picker-stores-with-stores"


def _valid1(val):
    if val:
        return (
            val.strip()
            .replace("–", "-")
            .encode("unicode-escape")
            .decode("utf8")
            .replace("\\xc3\\xa9", "e")
            .replace("\\xa0", "")
            .replace("\\xa0\\xa", "")
            .replace("\\xae", "")
        )
    else:
        return ""


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url)
        locations = res.json()
        for _ in locations:
            addr = parse_address_intl(_["location"]["formattedAddress"])
            hours = []
            for key, _hour in _["details"]["weeklySchedule"].items():
                temp = []
                for _time in _hour:
                    temp.append(f"{_time['from']}-{_time['to']}")
                if temp:
                    hours.append(f"{key}: {', '.join(temp)}")
            url = "-".join(
                [
                    line.strip()
                    for line in _["title"].lower().replace("-", "").strip().split(" ")
                    if line.strip() != ""
                ]
            )
            page_url = f"https://order.rolypoly.com/roly-poly-{url}/menu"
            yield SgRecord(
                store_number=_["storeId"],
                page_url=page_url,
                location_name=_["title"],
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=_["location"]["countryCode"],
                phone=_["details"]["contactInfo"]["phoneNumber"],
                latitude=_["location"]["latitude"],
                longitude=_["location"]["longitude"],
                locator_domain=locator_domain,
                location_type=_["type"],
                hours_of_operation=_valid1("; ".join(hours)),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
