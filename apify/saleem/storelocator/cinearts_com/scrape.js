const Apify = require('apify');

async function enqueueLocationLinks({ $, requestQueue }) {
  return Apify.utils.enqueueLinks({
    $,
    requestQueue,
    baseUrl: 'https://cinearts.com/theatres/',
    selector: '.theatres-by-state a',
  });
}

function scrapeLatLng($) {
  const src = $('.theatreMap img').attr('data-src');
  const match = src.match(/pp=(.*),(.*)&/i);
  if (match) {
    const [_, latitude, longitude] = match;
    return { latitude, longitude };
  } else {
    return {};
  }
}

async function scrape({ $, request }) {
  const scripts = $("script[type='application/ld+json']");
  const targetScript = scripts.length > 1 ? scripts[1] : scripts[0];
  try {
    const {
      name: location_name,
      address: [
        {
          streetAddress: street_address,
          addressLocality: city,
          addressRegion: state,
          postalCode: zip,
          addressCountry: country_code,
        },
      ],
      email,
      telephone: phone,
      '@type': location_type,
    } = JSON.parse(targetScript.children[0].data);

    const { latitude, longitude } = scrapeLatLng($);

    const store_number = parseInt(email.split('@')[0]);

    return {
      locator_domain: 'cinearts.com',
      page_url: request.url,
      location_name,
      street_address,
      city,
      state,
      zip,
      country_code,
      store_number,
      phone: phone.length > 0 ? phone : '<MISSING>',
      location_type,
      latitude: latitude || '<MISSING>',
      longitude: longitude || '<MISSING>',
      hours_of_operation: '<MISSING>',
    };
  } catch (err) {
    return null;
  }
}

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'http://cinearts.com/full-theatre-list',
    userData: {
      pageType: 'locations',
    },
  });

  const crawler = new Apify.CheerioCrawler({
    requestQueue,
    ignoreSslErrors: true,
    async handlePageFunction({ request, $ }) {
      switch (request.userData.pageType) {
        case 'locations':
          await enqueueLocationLinks({ $, requestQueue });
          break;
        default:
          const poi = await scrape({ $, request });
          if (poi) await Apify.pushData(poi);
      }
    },
  });

  await crawler.run();

  Object.entries(counts).map(([key, value]) => {
    if (value > 1) {
      console.log(key);
    }
  });
});
