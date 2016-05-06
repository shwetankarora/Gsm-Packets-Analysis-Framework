module.exports = {

Packet : class Packet{
    constructor(message){
        this.jsonMessage = JSON.parse(message);
    }

    get packetData(){
        return this.jsonMessage;
    }

    get smac(){
        return this.jsonMessage.smac;
    }

    get dmac(){
        return this.jsonMessage.dmac;
    }

    get ip(){
        return this.jsonMessage.ip;        
    }

    get port(){
        return this.jsonMessage.port;
    }

    get time(){
        return this.jsonMessage.time;
    }

    get tower(){
        return this.jsonMessage.tower;
    }

    get mcc(){
        return this.jsonMessage.tower.mcc;
    }

    get cellid(){
        return this.jsonMessage.tower.cell_id;
    }

    get mnc(){
        return this.jsonMessage.tower.mnc;
    }

    get networkProvider(){
        return this.jsonMessage.tower.service;
    }

    get lac(){
        return this.jsonMessage.tower.lac;
    }

    get packetID(){
        return this.jsonMessage._id;
    }
}
}
