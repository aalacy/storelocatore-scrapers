const Apify = require('apify');
const request = require('request-promise');

Apify.main(async () => {
    // Get input of your actor
    const input = await Apify.getInput();
    console.log('My input:');
    console.dir(input);

    // Do something useful here
    const html = await request('http://alohags.com/oahu.html');

    // And then save output
    const output = {
        html,
        crawledAt: new Date(),
    };
    console.log('My output:');
    console.dir(output);
    await Apify.setValue('OUTPUT', output);
});
