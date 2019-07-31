const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');

var url = 'https://catchairparty.com/locations/';

async function scrape(){

  return new Promise(async (resolve,reject)=>{
    request(url,(err,res,html)=>{

        if(!err && res.statusCode==200){

          var items=[];

            const $  =cheerio.load(html);

            var main = $('.location_top_main').children('.container').find('.row').children('.col-lg-4');




            function mainhead(i)

        {
          if(main.length>i)

            {

              var link = $(main[i]).find('h4').find('a').attr('href');
              var location_name = $(main[i]).find('h4').text();
              var temp_address = $(main[i]).find('p').html();
              var temp_address1 = temp_address.split('<br>');
              var temp_address2 = temp_address1[0];
              var temp_address3 = temp_address2.split(',');

              if(temp_address3.length == 3){
                var city = temp_address3[1];
                var address = temp_address3[0];
                var state_temp = temp_address3[2];
                var state_temp1 = state_temp.split(' ');
                var state = state_temp1[1];
                var zip = state_temp1[2];
              }
              else if (temp_address3.length == 2){
                 var address_temp = temp_address3[0];
                 var address_temp1 = address_temp.split(' ');

                 if(address_temp1.length == 5){
                   var address = address_temp1[0]+' '+address_temp1[1]+' '+address_temp1[2]+' '+address_temp1[3];
                   var city = address_temp1[4];
                 }
                 else if(address_temp1.length == 6){
                  var address = address_temp1[0]+' '+address_temp1[1]+' '+address_temp1[2]+' '+address_temp1[3]+' '+address_temp1[4];
                  var city = address_temp1[5];
                }
                
                else if(address_temp1.length == 8){
                  var address = address_temp1[0]+' '+address_temp1[1]+' '+address_temp1[2]+' '+address_temp1[3]+' '+address_temp1[5]+' '+address_temp1[6];
                  var city = address_temp1[7]
                }
                else if(address_temp1.length == 11){
                  var address = address_temp1[0]+' '+address_temp1[1]+' '+address_temp1[2]+' '+address_temp1[3]+' '+address_temp1[4]+' '+address_temp1[5]+' '+address_temp1[6]+' '+address_temp1[7]+' '+address_temp1[8];
                  var city = address_temp1[10];
                }
                
                 
                var state_temp = temp_address3[1];
                var state_temp1 = state_temp.split(' ');
                var state = state_temp1[1];
                var zip =  state_temp1[2];
              }
             // console.log(location_name);

              var phone_temp  = temp_address1[1];
              var phone_temp1 = phone_temp.split('|');
              var phone = phone_temp1[0];


             
              request(link,(err,res,html)=>{

                if(!err && res.statusCode==200){

                  const $  =cheerio.load(html);

                  var hour1 = $('.location_top_main').children('.container').find('.row').find('.col-lg-3').find('.about_catch_cnt').text().trim().replace('STORE HOURS','');
               
                  var hour = hour1.replace('Open 7 days a week:','').trim();

                

                  
                  items.push({  

                   locator_domain: 'https://catchairparty.com/', 

                    location_name: location_name, 

                    street_address: address,

                    city: city, 

                    state: state,

                    zip:  zip,

                    country_code: 'US',

                    store_number: '<MISSING>',

                    phone: phone,

                    location_type: 'catchairparty',

                    latitude: '<MISSING>',

                    longitude: '<MISSING>', 

                    hours_of_operation:hour
                  }); 
                  mainhead(i+1);  
                  
                }

              });
             
          
             

          } 

          else{
         
            resolve(items);
        
           }
        } 
        
        mainhead(0);
              

            }
              
 });



});

}

Apify.main(async () => {

    

  const data = await scrape();
  
  await Apify.pushData(data);

 

});
 