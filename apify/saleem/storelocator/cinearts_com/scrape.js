const Apify = require('apify');
const request = require('request-promise');
const cheerio = require('cheerio');

(async () => {
  const rootAddress = new URL('https://cinearts.com/full-theatre-list');
  const storePageList = [];
  const listPage = await request.get({
    url: rootAddress,
    rejectUnauthorized: false
  });
  let $ = cheerio.load(listPage);
  $('.contentMain h3').each( (_, elem) => {
    const state = $(elem).text().trim();
    $(elem).next().children('a').each( (_, elem) => {
      storePageList.push({
        url: (new URL($(elem).attr('href'), rootAddress.origin).href),
        userData: {state}
      })
    })
  })

  const requestList = new Apify.RequestList({
    sources: storePageList,
  });
  await requestList.initialize();

  const crawler = new Apify.CheerioCrawler({
    requestList,
    ignoreSslErrors: true,
    handlePageFunction: async ({ request, response, html, $ }) => {

      // Begin scraper
      
      const {
        name: location_name,
        address: [{
          streetAddress: street_address,
          addressLocality: city,
          addressRegion: state,
          postalCode: zip,
          addressCountry: country_code,
        }],
        '@id': store_number,
        telephone: phone,
        '@type': location_type
      } = JSON.parse($("script[type='application/ld+json']")[0].children[0].data);
			const poi = {
        locator_domain: 'cinearts.com',
        location_name,
        street_address,
        city,
        state,
        zip,
        country_code,
				store_number,
				phone,
				location_type,
        latitude: '<MISSING>',
        longitude: '<MISSING>',
				hours_of_operation: '<MISSING>'
			};

			await Apify.pushData([poi]);

			// End scraper

    },
  });

  await crawler.run();
})();
