from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.thenorthface.com.br"
urls = {
    "store": "https://www.thenorthface.com.br/api/dataentities/SL/search?_fields=id,nome,endereco,numero,complemento,bairro,cidade,estado,cep,email,telefone,celular,lat,lng,horario,tipo&an=thenorthface",
    "outlet": "https://www.thenorthface.com.br/api/dataentities/LM/search?_fields=id,nome,endereco,numero,complemento,bairro,cidade,estado,cep,email,telefone,celular,lat,lng,horario,tipo&an=thenorthface",
}


def fetch_data():
    with SgRequests() as session:
        for type, base_url in urls.items():
            locations = session.get(base_url, headers=_headers).json()
            for _ in locations:
                street_address = _["endereco"]
                if _.get("numero"):
                    street_address += ", " + _["numero"]
                yield SgRecord(
                    page_url="https://www.thenorthface.com.br/nossas-lojas",
                    store_number=_["id"],
                    location_name=_["nome"],
                    street_address=street_address,
                    city=_["cidade"],
                    zip_postal=_["cep"],
                    latitude=_["lat"],
                    longitude=_["lng"],
                    country_code="BR",
                    phone=_["telefone"],
                    location_type=type,
                    locator_domain=locator_domain,
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
