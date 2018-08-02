import Vue from 'vue'
import App from './App.vue'
import store from './store.js'
import '@voerro/vue-tagsinput/dist/style.css';

import moment from 'moment';
moment.updateLocale('ru', {calendar : {
        lastDay : '[Вчера]:LT',
        sameDay : '[Сегодня]:LT',
        nextDay : 'L:LT',
        lastWeek : 'L:LT',
        nextWeek : 'L:LT',
        sameElse : 'L:LT'},longDateFormat : {L:'DD.MM'}});

Vue.prototype.momentum = moment;

var vue_app = new Vue({
    el: '#app',
    render: h => h(App),
    store,
    data:{
        bus: new Vue({})
    },
});

window.vue_app = vue_app;

window.onfocus = function () {
    if (window.vue_app.$isMobile.any){
        // console.log('Mobile!');
        window.scrollTop = 0;
    }
};
