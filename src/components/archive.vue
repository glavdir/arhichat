<template>
<div class="archive_root">
    <div class="header archive_header">
        <div class="chat_users">
            <div class="activeusers">
                <div v-for="user in pmids" :key="user.userid"
                             v-bind="{'data-pmid': user.userid}"
                             v-bind:class="{tabUser:true, tabActive:user.userid==curpmid}"
                             v-html="user.userlook"
                             @click="tabOnClick(user.userid)">

                </div>
            </div>
        </div>
    </div>
    <div class='archive_main' ref="shouts">
        <div class="archive_shouts" >
            <div v-for="message in messages" :key="message.sid" class="msg" v-bind="{'data-sid': message.sid, key:message.sid}">
                <div v-if="isSearchResult" class="msg-link" @click="gotoMsg(message.sid)">Перейти</div>
                <chat-shout class="shout" v-bind="{'data-sid': message.sid}"
                                :sid="message.sid"
                                :me ="message.me"
                                :s_user ="message.s_user"
                                :user ="message.user"
                                :time ="message.time"
                                :color ="message.color"
                                :msg ="message.msg"
                    ></chat-shout>
            </div>
        </div>
    </div>
    <div class="archive_footer">
        <pages v-model="curPage" :pageCount="pageCount" @input="getShouts()"></pages>
        <div class="search_div">
            <input class="archive_search" type="text" placeholder="Поиск для бога поиска..." v-model="searchString" @change="doSearch">
            <button class ="submit_search icon-search" type="submit" @click="doSearch"><icon name="search"></icon></button>
        </div>
    </div>
</div>
</template>

<script>
    import shout  from './shout.vue';
    import pages  from './pages.vue';
    import global from '../global.js';
    import axios from 'axios';

    export default {
        data:function(){return {
            searchString: '',
            curPage: 1,
            count: 100,
            pageCount:1,
            messages:[],
            pmids:[{userid:-1,userlook:'ЧАТ'}],
            curpmid:-1,
            isSearchResult:false
        }},
        methods:{
            doSearch(){
                this.curPage = 1;
                this.getShouts();
            },
            getPmids(){
                let this_app = this;
                axios.get(global.curdomain + '/api/archive_pmids/', {withCredentials: true})
                    .then(function (response) {
                        let pmids = response.data;
                        pmids.unshift({userid:-1,userlook:'ЧАТ'});
                        this_app.pmids = pmids;
                    });
            },

            getShouts(sid=''){
                let this_app = this;
                let params = {page:this.curPage, count:this.count, search:this.searchString, pmid:this.curpmid};

                if (sid!=''){
                    params['sid'] = sid;
                }

                axios.get(global.curdomain + '/api/archive/', {withCredentials: true, params:params})
                    .then(function (response) {
                        this_app.messages = response.data.messages.slice().reverse();
                        this_app.pageCount = response.data.page_count;
                        this_app.isSearchResult = this_app.searchString!='';
                        this_app.curPage = response.data.page;
                        // if (this_app.pageCount<this_app.curPage) {
                        //     this_app.curPage = 1;
                        // }

                        this_app.$nextTick( function(){
                            if (sid!=''){
                                document.querySelector('div[data-sid="'+sid+'"]').scrollIntoView(true);
                            }else{
                                this_app.$refs.shouts.scrollTop = 0;
                            }
                        });
                    });
            },
            tabOnClick(userid){
                this.curpmid = userid;
                this.doSearch();
            },
            gotoMsg(sid){
                this.page = 1;
                this.searchString = '';
                this.getShouts(sid);
            }
        },
        created(){
            this.getPmids();
            this.getShouts();
        },
        components: {
            'pages':pages,
            'chat-shout':shout
        },
    }
</script>

<style scoped>
    .archive_root{
        width: 100%;
        height: 100%;
    }
</style>
