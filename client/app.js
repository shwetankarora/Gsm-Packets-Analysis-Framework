var MongoClient = require('mongodb').MongoClient;
var WebSocketClient = require('websocket').client;
var Packet = require('./packet.js').Packet;


// connecting to mongodb database and creating a handler
var db;
MongoClient.connect("mongodb://localhost:27017/GsmSimulatedData", function(err, client){
    if(err){
        console.log("[-]", err);
        client.close();
        process.exit();
    }
    else{
        db = client;
    }
});


// connecting to the websocket server
var client = new WebSocketClient();
client.connect("ws://localhost:6001");

var no_of_retries = 5;


// handling connection events
client.on('connect', function(connection){
    console.log('[*] Connected to 127.0.0.1:6001');
    connection.on('message', function(message){
        message = message.utf8Data;
        var p = new Packet(message);
        console.log(p.jsonMessage);
        /* store the raw packet in mongodb database GsmSimulatedData with collection as RawPackets  */
        var packets_collection = db.collection('RawPackets');
        packets_collection.insertOne(p.packetData, function(err, result){
            if(err){
                console.log("[-]",err);
                db.close();
                process.exit();
            }
            // console.log(result);
        });
    });
});


client.on('connectFailed', function(error){
    if(db != undefined){
        db.close();
    }
    setTimeout(function(){
	no_of_retries -= 1
	console.log("[-] WebSocket Server is not running.");
	console.log("[*] Reconnecting..... after 3 seconds");
	console.log("[*] No. of retries left ",no_of_retries);
	client.connect("ws://localhost:6001");
	if(!no_of_retries) { process.exit(); }
	}, 3000);
});


client.on('httpResponse', function(response, client){
    console.log("[-] Client is not able to make http requests and read http responses.");
    db.close();
    process.exit();
});
