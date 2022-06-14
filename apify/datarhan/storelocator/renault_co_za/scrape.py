# -*- coding: utf-8 -*-
import re
import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_urls = {
        "https://www.renault.co.za/FindAdealer.html": "https://rsidealerlocator.makolab.pl/service/dealers.svc/dealers/om?callback=jQuery110206533315599792127_1655043124218&_=1655043124219",
        "https://renault-iran.com/fa/dealer-locator.html": "https://rsidealerlocator.makolab.pl/service/dealers.svc/dealers/irfa?callback=jQuery110207490281710075513_1655043793176&_=1655043793177",
        "https://www.renault.co.ao/Localizadordeconcessionarios/dealerlocatorService.html": "https://rsidealerlocator.makolab.pl/service/dealers.svc/dealers/ao?callback=jQuery110207482514048850948_1655043822343&_=1655043822344",
        "https://www.renault.am/dealerlocatorService.html": "https://rsidealerlocator.makolab.pl/service/dealers.svc/dealers/am?callback=jQuery11020920551561219852_1655043857379&_=1655043857380",
        "https://www.renault.by/find-a-dealer.html": "https://rsidealerlocator.makolab.pl/service/dealers.svc/dealers/by?callback=jQuery110204309426362918687_1655043899665&_=1655043899666",
        "https://www.renault.bh/find-a-showroom.html": "https://rsidealerlocator.makolab.pl/service/dealers.svc/dealers/bh?callback=jQuery11020903996808321113_1655043929927&_=1655043929928",
        "https://www.renault.ec/contacto/concesionarios.html": "https://rsidealerlocator.makolab.pl/service/dealers.svc/dealers/ec?callback=jQuery110204257459073404659_1655043954831&_=1655043954832",
        "http://www.renault.com.eg/RenaultNetworks.html": "https://rsidealerlocator.makolab.pl/service/dealers.svc/dealers/eg?callback=jQuery110204255726635541117_1655043979045&_=1655043979046",
        "https://www.renault-guyane.fr/dealerlocatorService.html": "https://rsidealerlocator.makolab.pl/service/dealers.svc/dealers/gy?callback=jQuery1102026869797350140256_1655044005467&_=1655044005468",
        "https://www.renault.com.gr/dealerlocatorTool.html": "https://rsidealerlocator.makolab.pl/service/dealers.svc/dealers/gr?callback=jQuery110208498536356690947_1655044030699&_=1655044030700",
        "https://renault-guadeloupe.com/coordonnees.html": "https://rsidealerlocator.makolab.pl/service/dealers.svc/dealers/gp?callback=jQuery11020009891093372536242_1655044059178&_=1655044059179",
        "http://www.renault.com.gt/Agencia/Ubicacion.html": "https://rsidealerlocator.makolab.pl/service/dealers.svc/dealers/gt?callback=jQuery1102014325096109965707_1655044092938&_=1655044092939",
        "https://www.renault.co.id/contacts/dealerlist2.html": "https://rsidealerlocator.makolab.pl/service/dealers.svc/dealers/iden?callback=jQuery1102004411970646526142_1655044139736&_=1655044139737",
        "https://renault.iq/en/dealers.html": "https://rsidealerlocator.makolab.pl/service/dealers.svc/dealers/iqen?callback=jQuery11020948133070064717_1655044167183&_=1655044167184",
        "https://www.renault.co.il/r-dealerlocator.html": "https://rsidealerlocator.makolab.pl/service/dealers.svc/dealers/il?callback=jQuery11020582137105390311_1655044203018&_=1655044203019",
        "https://www.renault.kz/ru/find-a-dealer.html": "https://rsidealerlocator.makolab.pl/service/dealers.svc/dealers/kz?callback=jQuery1102030969841783744534_1655044255564&_=1655044255565",
        "https://www.renault-kuwait.com/find-a-showroom.html": "https://rsidealerlocator.makolab.pl/service/dealers.svc/dealers/kw?callback=jQuery110204625852779088926_1655044285453&_=1655044285454",
        "https://www.renault.lv/lv/dealerlocatorService.html": "https://rsidealerlocator.makolab.pl/service/dealers.svc/dealers/lv?callback=jQuery1102016502767959179687_1655044348455&_=1655044348456",
        "https://www.renault.lt/dealerlocatorService.html": "https://rsidealerlocator.makolab.pl/service/dealers.svc/dealers/lt?callback=jQuery110207833106846535312_1655044390318&_=1655044390319",
        "https://renault-liban.com/en/dealers.html": "https://rsidealerlocator.makolab.pl/service/dealers.svc/dealers/lben?callback=jQuery1102041302228307815136_1655044423228&_=1655044423229",
        "http://renault.md/dealerlocatorService.html": "https://rsidealerlocator.makolab.pl/service/dealers.svc/dealers/md?callback=jQuery110202744584011710487_1655044452964&_=1655044452965",
        "https://www.renault.com.om/find-a-showroom.html": "https://rsidealerlocator.makolab.pl/service/dealers.svc/dealers/om?callback=jQuery110207097744464633897_1655044525075&_=1655044525076",
        "https://www.renault.qa/find-a-showroom.html": "https://rsidealerlocator.makolab.pl/service/dealers.svc/dealers/qa?callback=jQuery1102020381225957843752_1655044561683&_=1655044561684",
        "https://www.renault.re/dealerlocatorService.html": "https://rsidealerlocator.makolab.pl/service/dealers.svc/dealers/re?callback=jQuery1102009569271260578138_1655044632115&_=1655044632116",
        "https://www.renault.tn/dealerlocatorService.html": "https://rsidealerlocator.makolab.pl/service/dealers.svc/dealers/tn?callback=jQuery110209423080771822565_1655044859156&_=1655044859157",
    }
    domain = "renault.co.za"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    for page_url, start_url in start_urls.items():
        response = session.get(start_url, headers=hdr)
        data = re.findall(r"jQuery.+?\((.+?)\);", response.text)[0]

        all_locations = json.loads(data)
        for poi in all_locations:
            street_address = poi["AddressLine1"]
            if poi["AddressLine2"]:
                street_address += " " + poi["AddressLine2"]
            if poi["AddressLine3"]:
                street_address += " " + poi["AddressLine3"]

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["DealerName"],
                street_address=street_address,
                city=poi["City"],
                state="",
                zip_postal=poi["Postcode"],
                country_code=poi["CountryName"],
                store_number=poi["UniqueId"],
                phone=poi["Phone"],
                location_type="",
                latitude=poi["Latitude"],
                longitude=poi["Longitude"],
                hours_of_operation="",
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
