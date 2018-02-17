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

    set_chat_users_width: function set_chat_users_width() {
        var elems = document.querySelectorAll('.chat_users');
        for (var i = 0; i < elems.length; i++ ){
           var newWidth = elems[i].parentElement.clientWidth;
           elems[i].setAttribute('style','max-width:'+newWidth+'px'); //'width:'+newWidth+'px;
        }
    },

    curdomain: 'http://' + document.domain + socketport
}
