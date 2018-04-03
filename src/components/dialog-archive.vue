<template>
<div class="dialog_archive_root">
    <div class="dialog_archive_header header">
        <div class="dialog_thread"><!--
            --><div class="dialog_thread_select">
                <multiselect
                    v-model="selThreads"
                    :options="threads"
                    :multiple="true"
                    :show-labels="false"
                    :allow-empty="true"
                    track-by="title"
                    :custom-label="customLabel"
                    placeholder = "Выберите канал..."
                    class="dats"
                    :limit="1"
                    :limit-text="limitText"
                    :close-on-select="false"
                    :clear-on-select="false"
                    @input = "changeThreads"
                >
                    <template slot="tag" slot-scope="props"><span class="custom__tag"><span>#{{props.option.threadid }} {{props.option.title}} </span></span></template>
                </multiselect>

            </div><!--
            --><div class="dialog_thread_buttons">
                <!--<pages v-model="page" :pageCount="pageCount" @input="changeThreads"></pages>-->
            </div>
        </div>
    </div>
    <div class="dialog_archive_main">
        <div class="dialog_archive_posts" ref="posts">
            <div class='dialog_archive_container'>
                <div  class="dialog_archive_replies">
                    <div class="reply" v-for = "(pst) in posts">
                        <div contenteditable="false" :data-postid="pst.postid" v-html="pst.pagetext"></div>
                        <a v-show="isSearchResult" class="postlink" :data-postid="pst.postid" @click="gotoPost(pst.postid)">Перейти</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="dialog_archive_footer">
        <pages v-model="page" :pageCount="pageCount" @input="changeThreads"></pages>
        <div class="dialog_archive_footer_splitter"></div>
        <div class="search_div">
            <input class="archive_search" type="text" placeholder="Поиск для бога поиска..." v-model="searchString" @change="doSearch">
            <button class ="submit_search icon-search" type="submit" @click="doSearch"></button>
        </div>
    </div>
</div>
</template>

<script>
    import global from '../global.js';
    import axios from 'axios';
    import multiselect from 'vue-multiselect';
    import pages from './pages';

    // import {scroller} from 'vue-scrollto/src/scrollTo'
    // const ScrollTo = scroller();

	export default {
		name: "dialog-archive",
        data: function() {return{
            posts: [],
            pageCount:1,
            page:1,
            threads:[],
            selThreads:[],
            searchString:'',
            startThread: 0,
            isSearchResult:false
        }},
        methods:{
            setThreads(data){
                this.threads = data.threads;
                this.startThread = data.threadid;
                this.selectThread();
            },
            customLabel (option) {
                return "#"+option.threadid + " " + option.title;
            },
            limitText(){
                return 'И еще '+ (this.selThreads.length-1) + '';
            },
            getPosts(postid='') {
                var this_app = this;
                if (this.selThreads.length > 0) {
                    var threadsstr='';

                    for (var thr in this.selThreads){
                        var add =  (threadsstr=='')? '' : ',';
                        threadsstr = threadsstr + add + this.selThreads[thr].threadid;
                    }

                    let params = {threads: threadsstr, page:this.page, search:this.searchString};

                    if (postid!=''){
                        params['postid']=postid;
                    }

                    axios.get(global.curdomain + '/api/posts_archive/', {withCredentials: true, params: params})
                        .then(function (response) {
                            // console.log(response.data);
                            this_app.posts = response.data.posts.slice().reverse();
                            this_app.pageCount = response.data.page_count;
                            this_app.isSearchResult = this_app.searchString!='';
                            this_app.page = response.data.page;

                            this_app.$nextTick( function(){
                                if (postid!=''){
                                    document.querySelector('div[data-postid="'+postid+'"]').scrollIntoView(true);
                                }else{
                                    this_app.$refs.posts.scrollTop = 0;
                                }
                            });
                        });
                }else{
                    this_app.posts = [];
                }
            },
            gotoPost(postid){
                this.page = 1;
                this.searchString = '';
                this.getPosts(postid);
            },
            doSearch(){
                this.page = 1;
                this.getPosts();
            },
            changeThreads(){
                this.getPosts()
            },
            selectThread(){
                if (this.startThread!=0){
                    this.selThreads.push(this.threads[global.findObject(this.threads,'threadid',this.startThread)]);
                }
                this.getPosts();
            }
        },
        computed:{
            // threads:function(){
            //     return this.$store.state.threads;
            // },
        },
        components: {
            'multiselect':multiselect,
            'pages':pages
        },
        created(){
            // if (this.$store.state.lastThreadid!=0){
            //     this.selectThread();
            // }else {
            //     this.openThread = (data) => {
            //         this.selectThread();
            //     };
            //     this.$bus.$on("openThread", this.openThread);
            // }
            var this_app = this;
            if (this.threads.length==0){
                axios.get(global.curdomain+'/api/threads/', {withCredentials:true})
                    .then(function (response) {
                        this_app.startThread = response.data.threadid;
                        this_app.setThreads(response.data);
                    });
            }
        },
        beforeDestroy: function() {
            // this.$bus.$off("openThread", this.openThread);
        },
    }
</script>

<style scoped>
    .dialog_archive_root{
        width: 100%;
        height: 100%;
    }

    .dialog_archive_header{
        padding-right: 0.5rem
    }

    .dialog_archive_main{
        width: 100%;
        height: calc(100% - 5.5rem - 2px);
    }

    .dialog_archive_posts{
        margin: 0.5rem;
        overflow-y: scroll;
        height: calc(100% - 0.5rem);
        box-sizing: border-box;
    }
    .dialog_archive_container{
        margin-right: 0.5rem;
    }
    .dialog_archive_footer{
        height: 2.5rem;
        box-sizing: border-box;
        display: flex;
    }

    .dialog_archive_footer_splitter{
        flex: 1;
    }

    .postlink{
        cursor: pointer;
        text-decoration: underline;
        color: #444;
    }
</style>
