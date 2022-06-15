from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    data = "<soap:Envelope xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xmlns:xsd='http://www.w3.org/2001/XMLSchema' xmlns:soap='http://schemas.xmlsoap.org/soap/envelope/'><soap:Body><GetListItems xmlns='http://schemas.microsoft.com/sharepoint/soap/'><listName>Degalines</listName><viewName></viewName><query><Query><OrderBy><FieldRef Name=\"ID\"/></OrderBy></Query></query><viewFields><ViewFields><FieldRef Name='fld_eil_nr' /><FieldRef Name='fld_degaline' /><FieldRef Name='fld_degalines_adresas' /><FieldRef Name='fld_gps_kordinates' /><FieldRef Name='fld_miestas_rajonas' /><FieldRef Name='fld_degal_operatoriu_tel_nr' /><FieldRef Name='fld_el_pasto_adresas' /><FieldRef Name='opt_95' /><FieldRef Name='opt_verva_95' /><FieldRef Name='opt_98' /><FieldRef Name='opt_d' /><FieldRef Name='opt_verva_d' /><FieldRef Name='opt_dz' /><FieldRef Name='opt_lpg' /><FieldRef Name='opt_adblue' /><FieldRef Name='opt_stop_cafe' /><FieldRef Name='opt_wc' /><FieldRef Name='opt_automatine_plovykla' /><FieldRef Name='opt_oras' /><FieldRef Name='opt_dulkiu_siurblys' /><FieldRef Name='opt_tir_parking' /><FieldRef Name='opt_tir_kolonele' /><FieldRef Name='opt_wifi' /><FieldRef Name='opt_keliu_vinjete' /></ViewFields></viewFields><rowLimit>0</rowLimit><queryOptions><QueryOptions></QueryOptions></queryOptions></GetListItems></soap:Body></soap:Envelope>"
    api = "https://www.orlen.lt/LT/Degalines/_vti_bin/Lists.asmx"
    r = session.post(api, headers=headers, data=data)
    tree = html.fromstring(r.content)
    divs = tree.xpath("//row")

    for d in divs:
        street_address = "".join(d.xpath("./@ows_fld_degalines_adresas")).strip()
        city = "".join(d.xpath("./@ows_fld_miestas_rajonas")).strip()
        country_code = "LT"
        store_number = "".join(d.xpath("./@ows_id")).strip()
        location_name = "".join(d.xpath("./@ows_fld_degaline")).strip()
        phone = "".join(d.xpath("./@ows_fld_degal_operatoriu_tel_nr")).strip()
        latitude, longitude = "".join(d.xpath("./@ows_fld_gps_kordinates")).split(", ")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.orlen.lt/"
    page_url = (
        "https://www.orlen.lt/LT/Degalines/Puslapiai/Degalin%c4%97s-Lenkijoje.aspx"
    )
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0",
        "Accept": "application/xml, text/xml, */*; q=0.01",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Content-Type": "text/xml;charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.orlen.lt",
        "Connection": "keep-alive",
        "Referer": "https://www.orlen.lt/LT/Degalines/Puslapiai/Degalin%c4%97s-Lenkijoje.aspx",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
