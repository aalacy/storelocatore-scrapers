from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "cosstores.com"
    start_url = "https://www.cosstores.com/en_eur/store-locator.html"

    all_countries = [
        "AF",
        "AX",
        "AL",
        "DZ",
        "AS",
        "AD",
        "AO",
        "AI",
        "AQ",
        "AG",
        "AR",
        "AM",
        "AW",
        "AU",
        "AT",
        "AZ",
        "BS",
        "BH",
        "BD",
        "BB",
        "BY",
        "BE",
        "BZ",
        "BJ",
        "BM",
        "BT",
        "BO",
        "BQ",
        "BA",
        "BW",
        "BV",
        "BR",
        "IO",
        "BN",
        "BG",
        "BF",
        "BI",
        "CV",
        "KH",
        "CM",
        "CA",
        "KY",
        "CF",
        "TD",
        "CL",
        "CN",
        "CX",
        "CC",
        "CO",
        "KM",
        "CG",
        "CD",
        "CK",
        "CR",
        "CI",
        "HR",
        "CU",
        "CW",
        "CY",
        "CZ",
        "DK",
        "DJ",
        "DM",
        "DO",
        "EC",
        "EG",
        "SV",
        "GQ",
        "ER",
        "EE",
        "ET",
        "FK",
        "FO",
        "FJ",
        "FI",
        "FR",
        "GF",
        "PF",
        "TF",
        "GA",
        "GM",
        "GE",
        "DE",
        "GH",
        "GI",
        "GR",
        "GL",
        "GD",
        "GP",
        "GU",
        "GT",
        "GG",
        "GN",
        "GW",
        "GY",
        "HT",
        "HM",
        "VA",
        "HN",
        "HK",
        "HU",
        "IS",
        "IN",
        "ID",
        "IR",
        "IQ",
        "IE",
        "IM",
        "IL",
        "IT",
        "JM",
        "JP",
        "JE",
        "JO",
        "KZ",
        "KE",
        "KI",
        "KP",
        "KR",
        "KW",
        "KG",
        "LA",
        "LV",
        "LB",
        "LS",
        "LR",
        "LY",
        "LI",
        "LT",
        "LU",
        "MO",
        "MK",
        "MG",
        "MW",
        "MY",
        "MV",
        "ML",
        "MT",
        "MH",
        "MQ",
        "MR",
        "MU",
        "YT",
        "MX",
        "FM",
        "MD",
        "MC",
        "MN",
        "ME",
        "MS",
        "MA",
        "MZ",
        "MM",
        "NA",
        "NR",
        "NP",
        "NL",
        "NC",
        "NZ",
        "NI",
        "NE",
        "NG",
        "NU",
        "NF",
        "MP",
        "NO",
        "OM",
        "PK",
        "PW",
        "PS",
        "PA",
        "PG",
        "PY",
        "PE",
        "PH",
        "PN",
        "PL",
        "PT",
        "PR",
        "QA",
        "RE",
        "RO",
        "RU",
        "RW",
        "BL",
        "SH",
        "KN",
        "LC",
        "MF",
        "PM",
        "VC",
        "WS",
        "SM",
        "ST",
        "SA",
        "SN",
        "RS",
        "SC",
        "SL",
        "SG",
        "SX",
        "SK",
        "SI",
        "SB",
        "SO",
        "ZA",
        "GS",
        "SS",
        "ES",
        "LK",
        "SD",
        "SR",
        "SJ",
        "SZ",
        "SE",
        "CH",
        "SY",
        "TW",
        "TJ",
        "TZ",
        "TH",
        "TL",
        "TG",
        "TK",
        "TO",
        "TT",
        "TN",
        "TR",
        "TM",
        "TC",
        "TV",
        "UG",
        "UA",
        "AE",
        "GB",
        "US",
        "UM",
        "UY",
        "UZ",
        "VU",
        "VE",
        "VN",
        "VG",
        "VI",
        "WF",
        "EH",
        "YE",
        "ZM",
        "ZW",
    ]

    for country in all_countries:
        data = session.get(
            f"https://api.storelocator.hmgroup.tech/v2/brand/cos/stores/locale/en_GB/country/{country}"
        ).json()
        all_locations = data["stores"]
        for poi in all_locations:
            hoo = []
            if poi.get("openingHours"):
                for e in poi["openingHours"]:
                    hoo.append(f'{e["name"]} {e["opens"]} - {e["closes"]}')
            hoo = " ".join(hoo)
            state = poi["address"].get("state")
            if not state and poi.get("region"):
                state = poi["region"]["name"]
            city = poi["address"].get("postalAddress")
            if not city:
                city = poi["city"]
            street_address = poi["address"]["streetName1"]
            if "," in city:
                street_address += ", " + city.split(",")[0].strip()
                city = city.split(",")[-1].split()[-1].strip()
            if city.split()[-1].isdigit():
                city = " ".join(city.split()[:-1])
            if street_address == city:
                city = ""
            if state == "(unknown)":
                state = ""
            zip_code = poi["address"]["postCode"].strip()
            if zip_code == "-":
                zip_code = ""

            item = SgRecord(
                locator_domain=domain,
                page_url=start_url,
                location_name=poi["name"],
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=poi["countryCode"],
                store_number=poi["storeCode"],
                phone=poi.get("phone"),
                location_type=poi.get("storeClass"),
                latitude=poi["latitude"],
                longitude=poi["longitude"],
                hours_of_operation=hoo,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
