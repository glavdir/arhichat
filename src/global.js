// console.log(location.port);

var socketport = (location.port==8080) ? ':5000' : location.port;

export default {
    findObject(array, attr, value){
        for (var i = 0; i < array.length; i++) {
            if (array[i][attr] == value) {
                return i;
            }
        }
        return -1;
    },
    curdomain: 'http://' + document.domain + socketport
}
