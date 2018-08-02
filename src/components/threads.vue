<template>
    <div class="threads_root">
        <!--<div class="threads_header header">-->
        <!--</div>-->
        <div class="threads_conteiner">
            <div v-show="isEdit">
                {{curForum.forumid}}
                <input v-model="curForum.title">
                <button @click="saveForum">Сохранить</button>
                <!--<button @click="delForum">Удалить</button>-->
                <button @click="canselEditForum">Отмена</button>
            </div>
            <div v-show="!isEdit" class="threads_forums">
                <template>
                    <div v-for="forum in orderedForums" :key="forum.order" :class="{threads_forum:true, threads_forum_root:forum.isRoot}">
                        <div class="threads_forum_title">{{forum.title}}</div>
                        <!--{{forum.title}}-->
                        <div class="threads_forum_buttons">
                            <div v-if="!forum.isMain">
                                <button @click="editForum(forum)">Изменить</button>
                                <button @click="newThread(forum)">Новый канал</button>
                            </div>
                            <div v-if="forum.isMain">
                                <button @click="newForum()">Новый модуль</button>
                            </div>
                        </div>
                        <!--<div v-show="forum.show" class="threads_threads">-->
                             <!--<div v-for="thread in forum.threads" class="threads_thread">{{thread.title}}</div>-->
                        <!--</div>-->
                    </div>
                </template>
            </div>
        </div>
    </div>
</template>

<script>
    import axios from 'axios';
    import global from '../global';
    // import forumEdit from './forum-edit'
    // import Vue from 'vue';
    // import VueCollapse from 'vue2-collapse';
    // Vue.use(VueCollapse);

    // import Vue from 'vue'
    // import VTooltip from 'v-tooltip'
    // Vue.use(VTooltip);

    export default {
        name:"threads",
        data:function(){return{
            forums:[],
            curForum:{forumid:'',title:''},
            isEdit:false
        }},
        methods: {
            loadForums(){
                let this_app = this;
                axios.get(global.curdomain+'/api/forums/', {withCredentials:true})
                    .then(function (response) {
                        this_app.forums  = response.data;
                        console.log(response.data);
                    });
            },
            editForum(forum){
                this.isEdit = true;
                this.curForum = forum;
            },
            delForum(forum){

            },
            newThread(forum){

            },
            canselEditForum(){
                this.isEdit = false;
            },
            saveForum(){
                let this_app = this;
                this.$socket.emit('save_forum',this.curForum,function (result) {
                    if (result && "forumid" in result){
                        this_app.isEdit = false;
                        // this_app.forums[result.forumid] = result;
                        this_app.curForum = result;
                        this_app.flash('Модуль '+result.title+' сохранен', 'success', {timeout: 2000});
                    }else{
                        let err = ("error" in result) ? result.error : '';
                        this_app.flash('ВНИМАНИЕ!<br>Что-то пошло не так и модуль не сохранен<br>'+err, 'error', {timeout: 10000});
                    }
                });
            },
            newForum(){
                this.editForum({forumid:0,title:'Новый'})
            }
        },
        computed: {
            orderedForums() {
                return this.forums.sort(function (firstItem,secondItem) {
                    if (firstItem.orrder>secondItem.order){
                        return 1;
                    }
                });
            }
        },
        components: {},
        created() {
            this.loadForums();
        }
    }
</script>
