<template>
    <div id="dc_app" class="wrapper">
        <auth v-if="$store.state.curuserid=='0'"></auth>
        <arh-panel v-if="isLeftPanel" ref="leftPanel" class="leftPanel"  :panel="leftPanel" :panelName="'left'" :altPanelName="'right'" :panels="panels"  :isAltPanel="isRightPanel" :style="leftSize">
             <kong v-if="isSplitter || isLeftPanel" slot="kong"></kong>
        </arh-panel>
        <div v-if="isSplitter" class="splitter">
            <div class="splitterHeader"></div>
        </div>
        <arh-panel v-if="isRightPanel" ref="rightPanel" class="rightPanel" :panel="rightPanel" :panelName="'right'" :altPanelName="'left'" :panels="panels" :isAltPanel="isLeftPanel" :style="rightSize">
            <kong  v-if="!isSplitter" slot="kong"></kong>
        </arh-panel>

        <div v-html="opts_censor"></div>
        <div v-html="opts_show_img"></div>
        <div v-html="opts_style"></div>
        <div v-html="opts_font_size"></div>
        <flash-message transitionIn="animated swing" class="flash-message-pool"></flash-message>
        <div id="relativeContainer" ref="relativeContainer"></div>
    </div>
</template>

<script>
    import Vue from /* webpackChunkName: "vue" */'vue';
    import global from './global';
    import axios from 'axios';
    import Panel from './components/panel.vue';
    import Kong from './components/kong.vue';
    import Chat from './components/chat.vue';
    import Dialog from './components/dialog.vue';
    import Auth from './components/auth.vue';

    import Notes from './components/notes';
    import VueRouter from 'vue-router';
    Vue.use(VueRouter);

    import VueSocketio from 'vue-socket.io';
    import io from 'socket.io-client'
    var socket = io.connect(global.curdomain, {reconnection: true, transports: [window.transport], timeout:30000});
    Vue.use(VueSocketio, socket);
    Object.defineProperty(Vue.prototype,"$bus",{get:function(){return this.$root.bus;}}); //Шина событий для обмена между компонентами

    import isMobile from 'ismobilejs'
    Object.defineProperty(Vue.prototype,"$isMobile",{get:function(){return isMobile}});

    import VueFlashMessage from 'vue-flash-message';
    Vue.use(VueFlashMessage);
    import 'vue-flash-message/dist/vue-flash-message.min.css';

    import Icon from 'vue-awesome/components/Icon'
    Vue.component('icon', Icon);
    import 'vue-awesome/icons/check'
    import 'vue-awesome/icons/trash'
    import 'vue-awesome/icons/close'
    import 'vue-awesome/icons/star'
    import 'vue-awesome/icons/star-o'
    import 'vue-awesome/icons/refresh'
    import 'vue-awesome/icons/chevron-right'
    import 'vue-awesome/icons/history'
    import 'vue-awesome/icons/angle-left'
    import 'vue-awesome/icons/angle-right'
    import 'vue-awesome/icons/angle-double-left'
    import 'vue-awesome/icons/angle-double-right'
    import 'vue-awesome/icons/plus'
    import 'vue-awesome/icons/floppy-o'
    import 'vue-awesome/icons/expand'
    import 'vue-awesome/icons/search'
    import 'vue-awesome/icons/expand'
    import 'vue-awesome/icons/compress'
    import 'vue-awesome/icons/cog'
    import 'vue-awesome/icons/commenting'
    import 'vue-awesome/icons/commenting-o'

    const router = new VueRouter({
        mode: 'history',
        routes: []
    });

    Vue.directive('focus', {
        inserted: function (el, binding, vnode) {
            Vue.nextTick(function () {
                el.focus()
            })
            console.log('!!');
        }
    });

    const panels = {
        Chat:    {title:'Чат',              component:Chat},
        Dialog:  {title:'Игра',             component:Dialog},
        Notes:   {title:'Заметки',          component:Notes},
        CharEdit:{title:'Персонажи',        component:() => import(/* webpackChunkName: "game" */ './components/characterEdit')},
        Archive: {title:'Архив чата',       component:() => import(/* webpackChunkName: "archive" */ './components/archive')},
        DialogArchive:{title:'Архив игры',  component:() => import(/* webpackChunkName: "archive" */ './components/dialog-archive')},
        Options: {title:'Настройки',        component:() => import(/* webpackChunkName: "options" */ './components/options')},
        Arhibash:{title:'Архибаш',          component:() => import(/* webpackChunkName: "bash" */ './components/arhibash')},
        Threads: {title:'Разделы',          component:() => import(/* webpackChunkName: "game" */ './components/threads')},
    };

    export default {
        router,
        name: 'app',
        data() {
            return {
                panels:panels
            }
        },
        methods:{
            switch_transport() {
                if (this.opts.transport_switch){
                    this.$socket.io.opts.transports = ['polling', 'websocket'];
                }
            },
        },
        sockets:{
            connect_error: function(err){
                this.switch_transport();
                console.log('err'+socket.connected);
            },
            reconnect_attempt:function() {
                this.switch_transport();
                console.log('reconnect_attempt'+socket.connected)
            },
            do_reload:function() {
                location.reload();
            },
          },
        computed:{
            opts(){
                return this.$store.state.opts;
            },
            local_opts(){
                return this.$store.state.local_opts;
            },
            hasPanelParams(){
                return ('left' in this.$route.query) || ('right' in this.$route.query)
            },
            leftPanel:function(){
                return this.panels[this.$store.state.panels.left];
            },
            rightPanel:function(){
                return this.panels[this.$store.state.panels.right];
            },
            isLeftPanel:function(){
                return this.leftPanel!=undefined; //this.$route.query.left in this.panels;
            },
            isRightPanel:function(){
                return this.rightPanel!=undefined;//this.$route.query.right in this.panels;
            },
            leftSize:function () {
                return 'flex:'+this.local_opts.left_rate+'%';
            },
            rightSize:function () {
                return 'flex:'+(100-this.local_opts.left_rate)+'%';
            },
            isSplitter:function(){
                return this.isLeftPanel && this.isRightPanel;
            },
            opts_censor(){
                return (this.opts.censor) ? "<style>.mat{display: none;}.cens{display: inline;}</style>" : "<style>.mat{display: inline;}.cens{display: none;}</style>";
            },
            opts_show_img(){
                return (this.opts.show_img) ? "<style>.img_false{display: none;}.img_true{display: inline;}</style>" : "<style>.img_false{display: inline;}.img_true{display: none;}</style>";
            },
            opts_style(){
                var style = (window.style!=undefined && window.style!='') ? window.style : this.opts.style;
                return '<link rel="stylesheet" href="../static/css/style/'+ style+'.css?'+ this.$store.state.revision+'">';
            },
            opts_font_size(){
                var font_size = (window.font_size!=undefined && window.font_size!='') ? window.font_size : this.local_opts.font_size;
                return "<style>html,input,button,textarea,select{font-size:"+ font_size+"px} .bttn{font-size:"+ (Number(font_size) + 3)+"px} </style>";
            },
        },
        components:{
            'arh-panel': Panel,
            'kong':Kong,
            'auth':Auth
        },
        created(){
            let this_app = this;
            this_app.$store.commit('setLocal_opts',localStorage.getItem('local_opts'));
            // this_app.$store.commit('setIsMobile',isMobile.any);

            if (this.$store.state.curuserid == 0){
                axios.get(global.curdomain+'/api/user_auth/', {withCredentials:true})
                    .then(function (response) {
                        this_app.$store.commit('setCuruserid',      response.data.userid);
                        this_app.$store.commit('setTimezoneoffset', response.data.timezoneoffset);
                        this_app.$store.commit('setOpts',           response.data.opts);
                        if (response.data.opts.use_polling){
                            this_app.$socket.io.opts.transports = ['polling'];
                        }
                        // if (response.data.userid=='0'){
                        //     this_app.$router.push({path: '/', query: {left:'Auth'}});
                        //     this_app.$store.commit('setPanel',{panel:'left',   param:'Auth'});
                        //     this_app.$store.commit('setPanel',{panel:'right',  param:undefined});
                        // }
                    });
            }

            if (this.hasPanelParams){
                this.$store.commit('setPanel',{panel:'left',  param:this.$route.query.left});
                this.$store.commit('setPanel',{panel:'right', param:this.$route.query.right});
            }

            if (isMobile.phone){
                this.momentum.updateLocale('ru', {calendar : {
                lastDay : 'L:LT',
                sameDay : 'LT',
                nextDay : 'L:LT',
                lastWeek : 'L:LT',
                nextWeek : 'L:LT',
                sameElse : 'L:LT'},longDateFormat : {L:'DD.MM'}});
            }
       },
    }
</script>

<style>
    .wrapper{
        display: flex;
        flex-direction: row;
        height: 100%;
        width: 100%;
        position: absolute;
    }

    .leftPanel{
        flex: 1;
        /*width: 100%;*/
        height: 100%;
        /*background: #41b883;*/
    }

    .rightPanel{
        flex: 1;
        /*width: 100%;*/
        height: 100%;
        /*background: #CFE7F0;*/
    }

    .splitter{
        width: 1px;
        background: rgba(0,0,0,.08);
        height: 100%;
    }

    .splitterHeader{
        width: 1px;
        background: rgba(0,0,0,.74);
        height: 2rem;
    }

    .flash-message-pool{
        position: absolute;
        right: 0.5rem;
        bottom: 0;
    }
</style>
