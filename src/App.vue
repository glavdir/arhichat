<template>
    <div id="dc_app" class="wrapper">
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
    </div>
</template>

<script>
    import Vue from 'vue';
    import global from './global';
    import axios from 'axios';
    import Panel from './components/panel.vue';
    import Kong from './components/kong.vue';
    import Chat from './components/chat.vue';
    import Dialog from './components/dialog.vue';
    import Options from './components/options.vue';
    import Archive from './components/archive';
    import Notes from './components/notes';
    import DialogArchive from './components/dialog-archive';
    import CharEdit from './components/characterEdit.vue';
    import Arhibash from './components/arhibash.vue';

    import VueRouter from 'vue-router';
    Vue.use(VueRouter);

    import VueSocketio from 'vue-socket.io';
    import io from 'socket.io-client'
    var socket = io.connect(global.curdomain, {reconnection: true, transports: [window.transport], timeout:30000});
    Vue.use(VueSocketio, socket);
    Object.defineProperty(Vue.prototype,"$bus",{get:function(){return this.$root.bus;}}); //Шина событий для обмена между компонентами

    import VueFlashMessage from 'vue-flash-message';
    Vue.use(VueFlashMessage);
    import 'vue-flash-message/dist/vue-flash-message.min.css';

    const router = new VueRouter({
        mode: 'history',
        routes: []
    });

    var panels = {
        Chat:    {title:'Чат',              component:Chat},
        Dialog:  {title:'Игра',             component:Dialog},
        Notes:   {title:'Заметки',          component:Notes},
        CharEdit:{title:'Персонажи',        component:CharEdit},
        Archive: {title:'Архив чата',       component:Archive},
        DialogArchive:{title:'Архив игры',  component:DialogArchive},
        Options: {title:'Настройки',        component:Options},
        Arhibash:{title:'Архибаш',          component:Arhibash},
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
            'kong':Kong
        },
        created(){
            var this_app = this;

            this_app.$store.commit('setLocal_opts',localStorage.getItem('local_opts'));
            // axios.get(global.curdomain+'/api/threads/', {withCredentials:true})
            //     .then(function (response) {
            //         // console.log(response.data);
            //         this_app.$store.commit('setThreads',        response.data.threads);
            //         this_app.$store.commit('setLastThreadid',   response.data.threadid);
            //         this_app.$bus.$emit('openThread',{threadid:response.data.threadid})
            //     });

            if (this.$store.state.curuserid == 0){
                axios.get(global.curdomain+'/api/user_auth/', {withCredentials:true})
                    .then(function (response) {
                        this_app.$store.commit('setCuruserid',      response.data.userid);
                        this_app.$store.commit('setTimezoneoffset', response.data.timezoneoffset);
                        this_app.$store.commit('setOpts',           response.data.opts);
                        if (response.data.opts.use_polling){
                            this_app.$socket.io.opts.transports = ['polling'];
                        }
                    });
            }
            if (this.hasPanelParams){
                this.$store.commit('setPanel',{panel:'left',  param:this.$route.query.left});
                this.$store.commit('setPanel',{panel:'right', param:this.$route.query.right});
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
