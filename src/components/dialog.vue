<template>
<div class="dialog_root">
    <div id='dialog_header' class="dialog_header header">
        <div class="dialog_thread"><!--
            --><div class="dialog_thread_select">
                <multiselect
                        v-model="curThread"
                        :options="threads"
                        :show-labels="false"
                        :allow-empty="false"
                        track-by="title"
                        :custom-label="customLabel"
                        placeholder = "Выберите канал..."
                        @input = "changeThread"
                        class="dts"
                ></multiselect>
            </div><!--
            --><div class="dialog_thread_buttons">
                <span @click="changeFav" :class="{favorite_tread:true,favorite_tread_true:curThread.isFav, favorite_tread_false:!curThread.isFav, header_link:true}"></span>
                <span @click="refreshThread" class="dialog_refresh header_link icon-arrows-cw"></span>
                <!--<span @click="test" class="dialog_refresh header_link icon-ok"></span>-->
            </div>
        </div>
    </div>
    <div class="dialog_main">
        <div class="dialog_posts" ref="dialog_posts">
            <div class='dialog_container'>
                <div  class="replies" ref="replies">
                    <template v-for = "(pst,pstkey) in posts">
                        <!--<div class="reply" contenteditable="true" :data-postid="pst.postid" v-html="nl2br(pst.pagetext)" @input="editPost(pst,pstkey,$event)"></div> pst.pagetext = $event editPost(pst,pstkey,$event) -->
                        <!--<post :content="pst.pagetext" @update="editPost(pst,pstkey,$event)"></post>-->
                        <medium-editor class="reply"
                                       :text='pst.pagetext'
                                       :options="{toolbar: false}"
                                       custom-tag='div'
                                       v-on:edit='editPost(pst,pstkey,$event)'/>
                    </template>
                </div>
                <div class="previews">
                    <template v-for="(prv,key) in prevs">
                        <div v-if="key!='usr_'+curuserid && prv.msg!=''"  :key="prv.userid">
                            <!--&lt;!&ndash;<div class="prwUser" v-html="$root.getUserLook(prv.userid)"></div>&ndash;&gt;-->
                            <div class="preview" v-html="nl2br(prv.msg)" v-bind="{'style':'color:'+prv.color}"></div>
                        </div>
                    </template>
                </div>
            </div>
        </div>
        <div class="dialog_senddiv" @keydown.enter.ctrl="sendDialogPost">
            <textarea class = "dialogEditor" ref="dialogEditor" v-model="dialogText"  @input="applyTextEdit" placeholder="Ответы для бога ответов...">
            </textarea>
            <div class="dialog_buttons">
                <button @click="sendDialogPost" class="bttn icon-ok" id="dialog_send" title="Отправить"></button>
                <div id="dialog-splitter-1" class="bttn-splitter"></div>
                <button @click="restoreText" class="bttn icon-history" id="dialog_history" title="Последний пост"></button>
                <div id="dialog-splitter-2" class="bttn-splitter"></div>
                <color-select class="bttn" @input="changeColor" v-model="threadColor" :colorlist="[['darkred','#993399','#6600FF','blue','navy']]"></color-select>
            </div>
        </div>
    </div>
</div>
</template>

<script>

import global from '../global.js';
import Vue from 'vue';
import diff_match_patch from 'diff-match-patch'
var dmp = new diff_match_patch.diff_match_patch();

function dialog_posts_scrollTop() {
    var objDiv = document.querySelector(".dialog_posts");//$("#dialog_posts");
    objDiv.scrollTop = objDiv.scrollHeight;
}

import color_select from './colorSelect.vue';
import multiselect from 'vue-multiselect';
import editor from 'vue2-medium-editor'

export default {
    data: function() {return{
        // threads:[],
        threadid:0,
        curThread:{isFav:false,threadid:0,title:'Канал не выбран'},
        dialogText: '',
        prevText:'',
        threadColor: '',
        posts: [],
        prevs: [],
        // startThread:0
    }},
    computed:{
        curuserid:function(){
            return this.$store.state.curuserid
        },
        threads:function () {
            return this.$store.state.threads;
        }
    },
    components: {
        'color-select': color_select,
        'multiselect':multiselect,
        'medium-editor':editor
    },
    sockets:{
        connect() {
            var this_app = this;
            this.$socket.emit('dialog_start', {threadid:this.threadid}, function (callback) {
                this_app.refreshThread();
            });
        },
        reconnect(){
            this.refreshThread();
        },
        dialog_message(data){
            this.insertMessage(data);
        },
        preview_message(data) {
            this.setPreview(data);
        },
        diff(data) {
            this.applyDiffsPrw(data);
        },
        dialog_change_commit(data){//Надо будет переделать на диффы
            var postnumber = global.findObject(this.posts,'postid',data.id);
            this.posts[postnumber].pagetext = data.msg;
        }
    },
    methods: {
        nl2br:function(str){
            return str.replace(/([^>])\n/g, '$1<br/>');
        },
        // setThreads(data){
        //     // this.threads = data.threads;
        //     this.$store.commit('setThreads',data.threads);
        //     this.threadid = data.threadid;
        //     this.setThreadByID(data.threadid)
        // },
        customLabel (option) {
            return "#"+option.threadid + " " + option.title
        },
        setThreadByID(threadid){
            this.curThread = this.threads[global.findObject(this.threads,'threadid',threadid)];
            this.threadid = this.curThread.threadid;
            this.refreshThread();
        },
        changeThread () {
            this.threadid = this.curThread.threadid;
            this.refreshThread();
            this.$socket.emit('set_last_thread', {threadid:this.threadid});
        },
        changeFav(){
            this.curThread.isFav = !this.curThread.isFav;
            this.$socket.emit('set_favorites', {'threadid':this.threadid});
        },
        refreshThread(){
            this.$store.commit('setLastThreadid',this.threadid);
            var this_app = this;
            this.$socket.emit('dialog_refresh',
                {threadid:this.threadid},
                function (cbk){
                // Vue.set(this_app,'posts',[]); //Небольшая подпорка, призванная принудительно обновить рендер постов
                // this_app.$nextTick(function () {
                    Vue.set(this_app,'posts',cbk.posts);
                    this_app.threadColor = cbk.color;
                    this_app.setAllPreviews(cbk.previews);
                    // this_app.$forceUpdate();
                    dialog_posts_scrollTop();
                // });
                });
        },
        applyDiffsPrw(data){
            if (data.userid != this.$store.state.curuserid) {
                var text_to_patch = (['usr_' + data.userid] in this.prevs) ? this.prevs['usr_' + data.userid].msg : '';
            } else {
                var text_to_patch = this.dialogText;// text_to_patch = this_app.dialogText;
            }
            data.msg = dmp.patch_apply(dmp.patch_fromText(data.diffs), text_to_patch)[0];
            // this_app.setPreview(data);
            this.setPreview(data);
        },
        setPreview(data){
            if(data.userid!=this.curuserid) {
                var dlg = document.querySelector(".dialog_posts");
                var is_scrolled = (dlg.scrollHeight - dlg.scrollTop) <= (dlg.clientHeight + 10); //dlg.scrollHeight == dlg.scrollTop;//
                Vue.set( this.prevs, 'usr_'+data.userid, data);
            }else{
                var focusElem = document.querySelector(':focus');
                var focusId = (focusElem==null) ? null : focusId = focusElem.className;
                //if (document.querySelector(':focus')!=null && document.querySelector(':focus').id=='dialogEditor'){
                if (focusId!='dialogEditor'){
                    // console.log(!!!);
                    this.setText(data.msg);
                }
                is_scrolled = false;
            }
            if (is_scrolled) {
                this.$nextTick(function () {
                    dialog_posts_scrollTop()
                });
            }
        },
        setAllPreviews(previews){
            this.prevs = {};
            // this.setText('');
            this.setPreview({userid:this.curuserid,msg:''});
            for (var prev in previews){
                this.setPreview(previews[prev]);
            }
        },
        changeColor(){
            this.$socket.emit('diff',{dialog_id:this.threadid, diffs:'', color:this.threadColor});//$('#dialog_textcolor').val()
            this.$socket.emit('set_color',{color:this.threadColor,threadid:this.threadid});
        },
        setText(text){
            this.dialogText = text;
            this.prevText = text;
        },
        restoreText(){
            this.setText(localStorage.getItem('last_dialog_text_'+this.threadid));
        },
        applyTextEdit(ev) {
            var diffs = dmp.patch_make(this.prevText,this.dialogText);
            this.$socket.emit('diff',{dialog_id:this.threadid, diffs:dmp.patch_toText(diffs), color:this.threadColor});
            this.prevText = this.dialogText;
            localStorage.setItem('last_dialog_text_'+this.threadid,this.dialogText);
        },
        sendDialogPost(){
            if (this.dialogText!='') {
                this.$socket.emit('send_text', {threadid: this.threadid, msg: this.dialogText, color: this.threadColor});
                this.$socket.emit('dialog_preview', {msg: '', color:''});
                this.setText('');
            }
        },
        insertMessage(data){
            this.posts.push(data);
            this.$nextTick(function () {
                dialog_posts_scrollTop() //Вот сюда надо будет добавить условие скроллить или нет
            });
        },
        get_msg_html(data, contenteditable) {
            // return "<div class='reply' id='"+data.id+"' contenteditable='"+contenteditable+"' style='color:"+data.color+"'>"+nl2br(data.msg)+"</div>";
        },
        editPost(pst,pstkey,event){
            pst.pagetext = event.event.target.innerHTML;
            this.$socket.emit('dialog_change', {msg:event.event.target.innerText, id:pst.postid, color:pst.color});//, color:event.event.target.style.color
        },
    },
    mounted(){
        // console.log(this.threadid);
        // if (this.threadid==0){
        //     this.setThreadByID(this.$store.state.lastThreadid);
        // }

        this.openThread = (data) => {
            this.$store.commit('setLastThreadid',data.threadid);
            this.setThreadByID(data.threadid);
            // if (this.threads.length!=0){
            //     this.setThreadByID(data.threadid);
            // }else {
		     //    this.startThread = data.threadid;
            // }
	    };
        this.$bus.$on("openThread", this.openThread);
    },
    beforeDestroy: function() {
        this.$bus.$off("openThread", this.openThread);
    },
    created(){
        if (this.threadid==0 && this.threads.length!=0){
            this.setThreadByID(this.$store.state.lastThreadid);
        }
        // var this_app = this;
        // if (this.threads.length==0){
            // axios.get(global.curdomain+'/api/threads/', {withCredentials:true})
            //     .then(function (response) {
            //         // if (this_app.startThread!=0){
            //         //     response.data.threadid = this_app.startThread;
            //         // };
            //         this_app.setThreads(response.data);
            //     });
        // }
        // else {
        //
        // }
    },
};

</script>

<style>
    .dialog_root{
        width: 100%;
        height: 100%;
    }
</style>
