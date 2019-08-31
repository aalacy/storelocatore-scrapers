const Apify = require('apify');

(async () => {
  const rootAddress = new URL('https://www.atmosphere.ca/campaigns/stores/store-locations.html');
  const requestList = new Apify.RequestList({
    sources: [{
      url: rootAddress.href,
      userData: { pageType: 'mainPage' }
    }],
  });
  await requestList.initialize();

  const requestQueue = await Apify.openRequestQueue();

  const crawler = new Apify.CheerioCrawler({
    requestList,
    requestQueue,
    handlePageFunction: async ({ request, response, html, $ }) => {

      // Begin scraper
      switch (request.userData.pageType) {
        case 'mainPage':
          $('.sc-sl-single_province ul.sc-sl-single-province_city_stores li.sc-sl-single-province_city_stores-store .sc-sl-single-province_city_stores-store_name a').each( async (_, element) => {
            await requestQueue.addRequest({
              url: (new URL($(element).attr('href'), rootAddress.origin)).href,
              userData: { pageType: 'storePage' }
            })
          });
          break;

        case 'storePage':
          const poiDetails = JSON.parse($('.sdt-store-details').attr('data-info'));
          const poi = {
            locator_domain: 'atmosphere.ca',
            location_name: $('.store-detail__content .sdt-store-details__title').text().trim(),
            phone: $('.store-detail__content .sdt-store-details__descr .sdt-store-details__phone').text().trim(),
            street_address: $('.store-detail__content .sdt-store-details__descr').children().remove().end().text().trim().slice(0, -1),
            city: poiDetails.address.town,
            state: poiDetails.address.province,
            zip: poiDetails.address.postalCode,
            country_code: 'CA',
            store_number: poiDetails.storeId,
            location_type: '<MISSING>',
            latitude: poiDetails.latitude,
            longitude: poiDetails.longitude,
            hours_of_operation: $('.sdt-store-details__accordion').text().trim().replace(/[\n\s\t]+/g, ' ')
          };
    
          await Apify.pushData([poi]);
          break;
      
        default:
          throw "scraper doesn't know how to handle page!"
      }        

			// End scraper

    },
  });

  await crawler.run();
})();
