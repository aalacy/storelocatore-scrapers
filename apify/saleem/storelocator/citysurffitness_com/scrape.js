const Apify = require('apify');
const request = require('request-promise');
const cheerio = require('cheerio');

(async () => {
  const rootAddress = new URL('https://www.citysurffitness.com');
  const sources = [];
  const userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Safari/605.1.15'
  const basePageHTML = await request.get({
    url: rootAddress,
    headers: {
      'User-Agent': userAgent
    }
  });
  const $ = cheerio.load(basePageHTML);
  $('.folder:contains("Locations") a').each((_, elem) => {
    sources.push({
      url: (new URL($(elem).attr('href'), rootAddress)).href,
      headers: {
        'User-Agent': userAgent
      }
    })
  })


  const requestList = new Apify.RequestList({
    sources,
  });
  await requestList.initialize();

  const crawler = new Apify.CheerioCrawler({
    requestList,
    handlePageFunction: async ({ request, response, html, $ }) => {
      
      // Begin scraper
      const {
        location: {
          addressTitle: location_name,
          addressLine1: street_address,
          addressLine2,
          addressCountry: country_code,
          markerLat: latitude,
          markerLng: longitude
        }
      } = JSON.parse($('.sqs-block-map').attr('data-block-json'))
      const {groups: { state, city, zip}} = addressLine2.match(/^[\s\n]*(?<city>[\D]*),\s(?<state>[A-Z]{2}),\s(?<zip>[\d-]*)[\s\n]*$/)
      const phone = $('p:nth-child(3)', $('.main-content .sqs-block-html')[1]).text().trim();


			const poi = {
        locator_domain: 'citysurffitness.com',
        location_name,
        street_address,
        city,
        state,
        zip,
        country_code,
				store_number: '<MISSING>',
				phone,
				location_type: '<MISSING>',
        latitude,
        longitude,
				hours_of_operation: '<MISSING>'
			};

			await Apify.pushData([poi]);

			// End scraper

    },
  });

  await crawler.run();
})();
