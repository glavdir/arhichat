import Vue from 'vue';
import Vuex from 'vuex';
import global from './global.js';
import axios from 'axios';

Vue.use(Vuex);

const store = new Vuex.Store({
    state: {
        opts: {
            style:'default',
            censor:true,
            show_img:false,
            transport_switch:false,
            use_polling:false,
            use_kong:false,
            show_kong:false,
            s_color:'black',
        },
        local_opts:{
            font_size:16,
            left_rate:55

        },
        users: [{userid: -1, userlook: 'ЧАТ', online: true, unread: false}],
        unreads: [],
        curuserid: 0,
        timezoneoffset:0,
        revision:'',
        panels:{
            left:'Chat',
            right:'Dialog',
            leftLast:'Chat',
            rightLast:'Dialog',
        },
        // threads:[],
        lastThreadid:0
    },
    mutations: {
        setPanel(state, data){
            state.panels[data.panel] = data.param;
            if (data.param!=undefined){
                state.panels[data.panel+'Last']=data.param;
            }
        },
        closePanel(state, data){
            state.panels[data.panel] = undefined;
        },
        openPanel(state, data){
            state.panels[data.panel] = state.panels[data.panel+'Last'];
        },
        setCuruserid(state,curuserid){
            state.curuserid = curuserid;
        },
        setOpts(state, opts) {
            state.opts = opts;
        },
        setLocal_opts(state, local_opts){
            if (local_opts){
                var ls = JSON.parse(local_opts);
                for (var key in ls){
                    state.local_opts[key] = ls[key];
                }
            }
        },
        setUsers(state, data) {
            data.unshift({userid: -1, userlook: 'ЧАТ', unread: false, online:true});

            let onlines = [];

            for (var ind in data) {
                data[ind].unread = ('usr_' + data[ind].userid) in state.unreads;
                onlines.push(data[ind].userid);
            }

            state.users = data;

            let thisState = state;

            let unreads = Object.keys(state.unreads).map(function (key) { return state.unreads[key]; });
            let difference = unreads.filter(x => onlines.indexOf(x) == -1 && x!=true); //Вычисляем разницу между онлайн и непрочитанными ЛС

            // console.log(unreads);
            // console.log(difference);

            axios.get(global.curdomain + '/api/users/', {withCredentials: true, params: {userid:difference.join(',')}})
                .then(function (response) {
                    let userlist = response.data;
                    for (let ind in userlist){
                        thisState.users.push({userid: userlist[ind].userid, userlook: userlist[ind].userlook, unread: true, online:false})
                    }
                });
        },

        setUserAttr (state, data) {
            // console.log(data.value);
            var ind = global.findObject(state.users, 'userid', data.userid);
            if (ind!=-1) {
                state.users[ind][data.attr] = data.value;
                Vue.set(state.users, ind, state.users[ind])
            }
        },
        setUnreads (state, data) {
            state.unreads = data;
            var copy_users = state.users.slice();
            for (var ind in copy_users){copy_users[ind].unread = ('usr_'+ copy_users[ind].userid) in state.unreads;}
            state.users = copy_users;
        },
        addUnread (state,userid) {
            state.unreads['usr_'+userid] = true;
            this.commit('setUserAttr', {userid:userid, attr:'unread', value:true});
        },
        delUnread (state,userid) {
            delete state.unreads['usr_'+userid];
            this.commit('setUserAttr', {userid:userid, attr:'unread', value:false});
        },
        setTimezoneoffset(state, timezoneoffset) {
            state.timezoneoffset = timezoneoffset;
        },
        setLastThreadid(state,threadid){
            state.lastThreadid = threadid;
        }
    },
    computed: {

    }
});

export default store;
