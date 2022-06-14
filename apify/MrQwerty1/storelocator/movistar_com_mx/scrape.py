from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_states():
    ids = set()
    params = {
        "p_p_id": "mx_movistar_col_cacs_portlet_CentrosAtencionClientesPortlet",
        "p_p_lifecycle": "2",
        "p_p_state": "normal",
        "p_p_mode": "view",
        "p_p_resource_id": "/cacs/states",
        "p_p_cacheability": "cacheLevelPage",
    }

    data = {
        "typeOfCcc": "1",
    }

    r = session.post(page_url, headers=headers, params=params, data=data)
    js = r.json()["data"]

    for j in js:
        ids.add(j.get("idEstado"))

    return ids


def get_params():
    par = set()
    states = get_states()
    params = {
        "p_p_id": "mx_movistar_col_cacs_portlet_CentrosAtencionClientesPortlet",
        "p_p_lifecycle": "2",
        "p_p_state": "normal",
        "p_p_mode": "view",
        "p_p_resource_id": "/cacs/cities",
        "p_p_cacheability": "cacheLevelPage",
    }

    for state in states:
        data = {
            "_mx_movistar_col_cacs_portlet_CentrosAtencionClientesPortlet_stateId": state,
            "_mx_movistar_col_cacs_portlet_CentrosAtencionClientesPortlet_typeOfCcc": "1",
        }

        r = session.post(page_url, params=params, headers=headers, data=data)
        js = r.json()["data"]

        for j in js:
            city = j
            par.add((state, city))

    return par


def fetch_data(sgw: SgWriter):
    params = {
        "p_p_id": "mx_movistar_col_cacs_portlet_CentrosAtencionClientesPortlet",
        "p_p_lifecycle": "2",
        "p_p_state": "normal",
        "p_p_mode": "view",
        "p_p_resource_id": "/cacs/details",
        "p_p_cacheability": "cacheLevelPage",
    }

    pars = get_params()
    for s, c in pars:
        data = {
            "_mx_movistar_col_cacs_portlet_CentrosAtencionClientesPortlet_stateId": s,
            "_mx_movistar_col_cacs_portlet_CentrosAtencionClientesPortlet_city": c,
            "_mx_movistar_col_cacs_portlet_CentrosAtencionClientesPortlet_typeId": "1",
        }
        r = session.post(page_url, params=params, headers=headers, data=data)
        js = r.json()["data"]

        for j in js:
            street_address = j.get("direccion") or ""
            street_address = " ".join(
                street_address.replace("S/N.", "").replace("S/N", "").split()
            )
            city = j.get("ciudad")
            state = j.get("estado")
            postal = j.get("cp")
            country_code = "MX"
            store_number = j.get("id")
            location_name = j.get("nombreCac")
            phone = j.get("Phone")
            latitude = j.get("latitud")
            longitude = j.get("longitud")

            _tmp = []
            days = {"lunesviernes": "Mon-Fri", "HorarioDomingo": "Sun", "sabado": "Sat"}
            for key, day in days.items():
                inter = j.get(key)
                if inter:
                    _tmp.append(f"{day}: {inter}")

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                store_number=store_number,
                hours_of_operation=hours_of_operation,
                locator_domain=locator_domain,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.movistar.com.mx/"
    page_url = "https://www.movistar.com.mx/atencion-al-cliente/informacion/centros-de-atencion-a-clientes"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.movistar.com.mx",
        "Connection": "keep-alive",
        "Referer": "https://www.movistar.com.mx/atencion-al-cliente/informacion/centros-de-atencion-a-clientes",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
