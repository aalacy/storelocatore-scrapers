from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://deloitte.com/us"
base_url = "https://www2.deloitte.com/content/dam/Deloitte/resources/office-details.js?pageType=officelocator&cupagepath=%2Ftr%2Fen%2Ffooterlinks%2Foffice-locator"
prefecture_url = "https://en.wikipedia.org/wiki/Prefectures_of_Japan"


def fetch_data():
    with SgRequests() as session:
        prefectures = []
        for pref in bs(
            session.get(prefecture_url, headers=_headers).text, "lxml"
        ).select("table.wikitable.sortable tbody tr"):
            if pref.th:
                continue
            prefectures.append(pref.select("td")[1].text.strip())

        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            raw_address = _["CompleteAddress"].replace("N/A", "")
            page_url = f"https://deloitte.com{_['addressLink']}"
            addr = parse_address_intl(_["CompleteAddress"])
            zip_postal = _.get("postalcode")
            state = _.get("state")
            city = _["city"]
            country_code = _["country"]
            if zip_postal == "0000" or zip_postal == "N/A":
                zip_postal = ""
            if not zip_postal and addr.postcode and addr.postcode != "0000":
                zip_postal = addr.postcode
            if not state and addr.state:
                state = addr.state
            if addr.city:
                city = addr.city

            if not country_code and addr.country:
                country_code = addr.country

            _addr = raw_address.split(",")
            if country_code in ["United Kingdom", "Uruguay", "Netherlands", "Cyprus"]:
                zip_postal = _addr[-2].replace(".", "")
                city = _addr[-3]
                street_address = ", ".join(_addr[:-3])
            elif country_code in ["Venezuela", "Papua New Guinea"]:
                state = _addr[-2]
                city = _addr[-3]
                street_address = ", ".join(_addr[:-3])
            elif country_code == "US Virgin Islands":
                state = _addr[-2].strip().split()[0]
                zip_postal = _addr[-2].strip().split()[-1]
                city = _addr[-3]
                street_address = ", ".join(_addr[:-3])
            elif country_code == "Cayman Islands":
                zip_postal = _addr[-2]
                state = _addr[-3]
                city = _addr[-5]
                street_address = ", ".join(_addr[:-5])
            elif country_code == "Côte d'Ivoire":
                state = _addr[-2]
                zip_postal = _addr[-3]
                city = _addr[-4]
                street_address = ", ".join(_addr[:-4])
            elif country_code == "Brazil":
                state = _addr[-2]
                city = _addr[-3]
                zip_postal = _addr[-4]
                street_address = ", ".join(_addr[:-4])
            elif country_code == "日本":
                for pref in prefectures:
                    if pref in raw_address:
                        state = pref
                        break
                zip_postal = ""
                street_address = _city = raw_address
                if state:
                    street_address = _city = raw_address.replace(state, "")
                if "市" in _city:
                    _city = _city.split("市")
                    if len(_city) > 1:
                        city = _city[0] + "市"
                if city:
                    street_address = street_address.replace(city, "")
                if state == "東京都":
                    city = state
                    state = ""
            else:
                street_address = _["addressline1"]
                if _.get("addressline2"):
                    street_address += " " + _["addressline2"]
                if (
                    _.get("addressline3")
                    and city not in _["addressline3"]
                    and "Tel" not in _["addressline3"]
                ):
                    street_address += " " + _["addressline3"]
                if (
                    _.get("addressline4")
                    and city not in _["addressline4"]
                    and "Fax" not in _["addressline4"]
                ):
                    street_address += " " + _["addressline4"]

                if "Postal" in street_address:
                    if not zip_postal:
                        zip_postal = (
                            street_address.split("Postal")[-1].replace(":", "").strip()
                        )
                    street_address = street_address.split("Postal")[0].strip()

            if country_code == "Malaysia":
                if zip_postal and state and zip_postal in state:
                    state = state.replace(zip_postal, "").strip()
            elif country_code == "中国":
                state = ""
                street_address = street_address.replace("中国", "")
                if "澳门" in street_address:
                    city = "澳门"
                    street_address = street_address.replace("澳门", "")
                if "香港" in street_address:
                    city = "香港"
                    street_address = street_address.replace("香港", "")
                if "市" in street_address:
                    _ss = street_address.split("市")
                    street_address = _ss[-1]
                    city = _ss[0] + "市"
            elif country_code == "Oman":
                zip_postal = zip_postal.replace("Oman", "").replace(",", "")
            elif country_code == "United Arab Emirates":
                if state and state.isdigit():
                    state = ""

            phone = _.get("phoneNo")
            if phone:
                phone = phone.split(":")[-1].strip()

            latitude = _.get("geoLat")
            longitude = _.get("geoLng")
            if latitude == "0.0":
                latitude = ""
            if longitude == "0.0":
                longitude = ""
            yield SgRecord(
                page_url=page_url,
                location_name=_["officetitle"] + " Office",
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                latitude=latitude,
                longitude=longitude,
                country_code=country_code,
                phone=phone,
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.CITY,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
