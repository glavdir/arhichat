<template>
<div class="archive_root">
    <div class="header archive_header">
        <pages v-model="curPage" :pageCount="pageCount" @input="getShouts"></pages>
        <div class="archive_header_flex"></div>
        <div class="search_div">
            <input class="archive_search" type="text" placeholder="Поиск для бога поиска..." v-model="searchString" @change="doSearch">
            <button class ="submit_search icon-search" type="submit" @click="doSearch"></button>
        </div>
    </div>
    <div class='archive_main'>
        <div class="archive_shouts">
            <div v-for="message in messages" :key="message.sid" class="msg" v-bind="{'data-sid': message.sid, key:message.sid}">
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
            // dispPage: ''
        }},
        methods:{
            doSearch(){
                this.curPage = 1;
                this.getShouts();
            },
            getShouts(){
                var this_app = this;
                axios.get(global.curdomain + '/api/archive/', {withCredentials: true, params:{page:this.curPage, count:this.count, search:this.searchString}})
                    .then(function (response) {
                        this_app.messages = response.data.messages.slice().reverse();
                        this_app.pageCount = response.data.page_count;
                        if (this_app.pageCount<this_app.curPage) {
                            this_app.curPage = 1;
                            // this_app.getShouts();
                        }
                    });
            }
        },
        created(){
            this.getShouts()
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
    .archive_main{
        height: calc(100% - 3.5rem);
        overflow-y: auto;
        margin: 0.5rem;
        box-sizing: border-box;
    }

    .archive_header{
        display: flex;
        width: 100%;
    }

    .archive_header_flex{flex: 1}
</style>
