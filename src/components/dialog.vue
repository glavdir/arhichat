<template>
<div class="dialog_root">
    <div class="dialog_header header" ref="header">
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
                <span @click="changeFav" class="favorite_tread icon-conteiner header_link"><icon :name = "favIcon"></icon></span>
                <span @click="refreshThread" class="dialog_refresh icon-conteiner header_link"><icon name = "refresh"></icon></span>
                <!--<span @click="test" class="dialog_refresh header_link icon-ok"></span>-->
            </div>
        </div>
    </div>
    <div class="dialog_main">
        <div class="dialog_posts" ref="dialog_posts" v-show="dialogShow">
            <click-outside class='dialog_container' :handler="handleClickOutside">
                <div  class="replies" ref="replies">
                    <template v-for = "(pst,pstkey) in posts">
                        <div class="post">
                            <div v-if="curPost==pst.postid" class="post_toolbar">
                                <div class="post_toolbar_buttons">
                                    <button
                                        @click="commentingPost(pst)"
                                        class="bttn icon-conteiner" title="Комментировать пост"><icon name="commenting-o"></icon>
                                    </button>

                                    <color-select title="Изменить цвет" class="bttn icon-conteiner" v-model="pst.color" @input="changePostColor(pst)" :colorlist="[['darkred','#993399','#6600FF','blue','navy']]"></color-select>

                                    <button
                                        @click="delPostStart(pst)"
                                        class="bttn icon-conteiner" title="Удалить пост"><icon name="trash"></icon>
                                    </button>
                                    <button
                                        v-show="delConfirm"
                                        @click="delPostConfirm(pst)"
                                        class="bttn icon-conteiner" title="Подтвердить удаление">ОК
                                    </button>
                                </div>
                            </div>
                            <medium-editor
                                           class="reply"
                                           :text='pst.pagetext'
                                           :options="postEditorOpts"
                                           custom-tag='div'
                                           data-placeholder=" "
                                           @focus="focusPost(pst)"
                                           @blur="blurPost(pst)"
                                           @edit='editPost(pst,pstkey,$event)'
                            />
                            <div v-if="pst.comments.length!=0" class="post_comments">
                                <div v-for = "(cmt,cmtkey) in pst.comments" class="post_comment" :style="'color:'+cmt.color">
                                    <div class="post_comment_user">{{cmt.username}}:</div><div class="post_comment_text" v-html="cmt.text"></div>
                                </div>
                            </div>
                            <!--<div v-if="curPost!=pst.postid" class="reply" v-html="pst.pagetext" @click="postClick(pst)"></div>-->
                        </div>
                    </template>
                </div>
                <div class="previews">
                    <!--{{prevs}}-->
                    <template v-for="(prv,key) in prevs">
                        <div v-if="key!='usr_'+curuserid && prv.msg!=''"  :key="prv.userid">
                            <!--<div v-if = "prv.isCommenting" class="prwUser" v-html="$root.getUserLook(prv.userid)"></div>-->
                            <div v-show="!isBlank(prv.msg)" :class="{preview:true, isCommenting:prv.isCommenting}" v-html="nl2br(prv.msg)" v-bind="{'style':'color:'+prv.color}"></div>
                        </div>
                    </template>
                </div>
            </click-outside>
        </div>
        <div class="dialog_splitter" v-show="dialogShow"></div>
        <div class="dialog_senddiv" @keydown.enter.ctrl="sendDialogPost" @keydown.ctrl.*="changeCommenting" :class="{dialogCommenting:isCommenting}">
            <medium-editor :class="{dialogEditor:true, dialogEditorPlaceholder:isBlank(dialogText)}"
                           ref="dialogEditor"
                           :text="dialogText"
                           :options="editorOpts"
                           custom-tag='div'
                           :data-placeholder="isCommenting ? 'Комментарии для бога комментариев' : 'Ответы для бога ответов'"
                           v-on:edit='applyTextEdit($event)'/>
            <div v-if="isThreadSettings" class="thread_settings">
                <p>ID заметок </p><input v-model="noteID" @change="setNoteID">
            </div>
            <div class="dialog_buttons_conteiner">
                <div class="dialog_buttons_wrapper">
                    <div class="dialog_buttons">
                        <button @click="sendDialogPost" class="bttn icon-conteiner" id="dialog_send" title="Отправить"><icon name="check"></icon></button>
                        <button @click="restoreText" class="bttn icon-conteiner" id="dialog_history" title="Последний пост"><icon name="history"></icon></button>
                        <color-select class="bttn icon-conteiner" @input="changeColor" v-model="threadColor" :colorlist="[['darkred','#993399','#6600FF','blue','navy']]"></color-select>
                        <div class="dialog_buttons_splitter">{{commentingPostid}}</div>
                        <button @click="openThreadSettings" class="bttn icon-icon-conteiner" title="Настройки канала"><icon name="cog"></icon></button>
                        <button @click="changeCommenting"  class="bttn icon-icon-conteiner" title="Комментировать (Ctrl+*)"><icon :name="isCommenting ? 'commenting':'commenting-o'"></icon></button>
                        <!--<button @click="collapseDialog" class="bttn icon-conteiner" title="Свернуть игру"><icon name="expand"></icon></button>-->
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
</template>

<script>

import global from '../global.js';
import Vue from 'vue';
import axios from 'axios';
import diff_match_patch from 'diff-match-patch'
import deltaToBB from '../quillDeltaToBB.js';

let dmp = new diff_match_patch.diff_match_patch();

import HTML2BBCode from 'html2bbcode'
let converter = new HTML2BBCode.HTML2BBCode({weaknewline:false});

function dialog_posts_scrollTop() {
    let objDiv = document.querySelector(".dialog_posts");//$("#dialog_posts");
    objDiv.scrollTop = objDiv.scrollHeight;
}

import color_select from './colorSelect.vue';
import multiselect from 'vue-multiselect';
// import editor from 'vue2-medium-editor'
import editor from '../MediumEditor.js'
import clickOutside from 'onclick-outside';

var vueApp;

var toNotes = editor.MediumEditor.extensions.button.extend({
    name: 'toNotes',
    tagNames: ['mark'],
    contentDefault: '<b>N</b>',
    aria: 'Сохранить в заметках',
    action: 'toNotes',
    init: function () {
        editor.MediumEditor.extensions.button.prototype.init.call(this);
    },
    handleClick: function (event) {
        console.log(vueApp.curThread);
        let textToNotes = window.getSelection().toString();
        let noteId = vueApp.noteID;
        axios.post(global.curdomain+'/api/to_notes/','to_notes',{withCredentials:true, params:{text:textToNotes, id:noteId} })
            .then(function (response) {
                if (response.data=='ok'){
                    vueApp.flash('Сохранено в заметках', 'success', {timeout: 2000});
                }else{
                    vueApp.flash('Возможно не сохранено, ошибка: '+response.data, 'error', {timeout: 20000});
                }
            });
    }
});

export default {
    data: function() {return{
        dialogShow:true,
        editablepost:0,
        curPost:0,
        threads:[],
        threadid:0,
        curThread:{isFav:false,threadid:0,title:'Канал не выбран'},
        noteID:'',
        dialogText: '',
        prevText:'',
        threadColor: '',
        posts:[],
        prevs:[],
        startThread:0,
        delConfirm:false,
        isThreadSettings:false,
        isCommenting:false,
        commentingPostid:'',
        editorOpts:{
           // elementsContainer:document.querySelector('#relativeContainer'),
           toolbar:{
                buttons:['bold','italic','underline','toNotes'],
                diffTop: (this.$isMobile.any) ? -50 : -10
            },
            paste: {
                forcePlainText:false,
                cleanPastedHTML:true,
                cleanAttrs:['class', 'style', 'dir', 'text-align'],
                unwrapTags:['font']
            },
            placeholder: false,
            extensions: {'toNotes': new toNotes()}
        },
        postEditorOpts:{
            toolbar:{
                buttons:['bold','italic','underline', 'toNotes'],
                diffTop: (this.$isMobile.any) ? -50 : -10,
                // relativeContainer:document.querySelector('#relativeContainer')
            },
            paste: {forcePlainText:false},
            placeholder: false,
            extensions: {'toNotes': new toNotes()}
        },
        // quillOpts:{
        //     theme:'bubble'
        // }
    }},
    computed:{
        curuserid:function(){
            return this.$store.state.curuserid
        },
        favIcon:function () {
            return (this.curThread.isFav) ? 'star' : 'star-o';
        },
        isToolbar:function(){
            return this.curPost!=0;
        }
    },
    components: {
        'color-select': color_select,
        'multiselect':multiselect,
        'medium-editor':editor,
        clickOutside
    },
    sockets:{
        connect() {
            let this_app = this;
            this.loadThreads();
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
            let postnumber = global.findObject(this.posts,'postid',data.id);
            this.posts[postnumber].pagetext = data.msg;
        },
        post_deleted(data){
            let postnumber = global.findObject(this.posts,'postid',data.postid);
            this.posts.splice(postnumber,1);
        },
        dialog_comment(data){
            this.insertComment(data);
        }
    },
    methods: {
        startPostEdit(postid){
            this.editablepost = postid;
        },
        isBlank(ev){
            return ev=='' || ev=='<p></p>' || ev=='<p><br></p>';
        },
        toBB(html, color=''){
            let res = converter.feed(html).s;
            if (color!=''){
                res = '[color='+color+']'+res+'[/color]';
            }
            return res;
        },
        nl2br:function(str){
            return global.nl2br(str);// str.replace(/([^>])\n/g, '$1<br/>');
        },
        setThreads(data){
            this.threads = data.threads;
            // this.$store.commit('setThreads',data.threads);
            this.threadid = data.threadid;
            this.setThreadByID(data.threadid)
        },
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
            this.setLastThread(this.threadid);
        },
        setLastThread(threadid){
            this.$socket.emit('set_last_thread', {threadid:threadid});
        },

        changeFav(){
            this.curThread.isFav = !this.curThread.isFav;
            this.$socket.emit('set_favorites', {'threadid':this.threadid});
        },
        refreshThread(){
            // toNotesThreadID = this.threadid;
            this.$store.commit('setLastThreadid',this.threadid);
            let this_app = this;
            this.$socket.emit('dialog_refresh',
                {threadid:this.threadid},
                function (cbk){
                    // console.log(cbk.previews);
                    Vue.set(this_app,'posts',cbk.posts);
                    this_app.threadColor = cbk.color;
                    this_app.noteID = cbk.noteID;
                    this_app.isCommenting = cbk.is_commenting;
                    this_app.commentingPostid = '';
                    this_app.setAllPreviews(cbk.previews);
                    dialog_posts_scrollTop();
                // });
                });
        },
        applyDiffsPrw(data){
            let text_to_patch = '';
            if (data.userid != this.$store.state.curuserid) {
                text_to_patch = (['usr_' + data.userid] in this.prevs) ? this.prevs['usr_' + data.userid].msg : '';
            } else {
                text_to_patch = this.dialogText;// text_to_patch = this_app.dialogText;
            }
            data.msg = dmp.patch_apply(dmp.patch_fromText(data.diffs), text_to_patch)[0];
            // this_app.setPreview(data);
            this.setPreview(data);
        },
        setPreview(data){
            let is_scrolled = false;
            if(data.userid!=this.curuserid) {
                let dlg = document.querySelector(".dialog_posts");
                is_scrolled = (dlg.scrollHeight - dlg.scrollTop) <= (dlg.clientHeight + 10); //dlg.scrollHeight == dlg.scrollTop;//
                Vue.set( this.prevs, 'usr_'+data.userid, data);
            }else{
                let focusElem = document.querySelector(':focus');
                let focusId = (focusElem==null) ? null : focusId = focusElem.className;
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
            for (let prev in previews){
                this.setPreview(previews[prev]);
            }
        },
        changeColor(){
            this.$socket.emit('diff',{dialog_id:this.threadid, diffs:'', color:this.threadColor, isCommenting:this.isCommenting});//$('#dialog_textcolor').val()
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
            let text = ev.event.target.innerHTML;
            let diffs = dmp.patch_make(this.dialogText,text);
            this.$socket.emit('diff',{dialog_id:this.threadid, diffs:dmp.patch_toText(diffs), color:this.threadColor, isCommenting:this.isCommenting});
            this.dialogText = text;
            localStorage.setItem('last_dialog_text_'+this.threadid,this.dialogText);
            // var diffs = dmp.patch_make(this.prevText,this.dialogText);
            // this.$socket.emit('diff',{dialog_id:this.threadid, diffs:dmp.patch_toText(diffs), color:this.threadColor});
            // this.prevText = this.dialogText;
            // localStorage.setItem('last_dialog_text_'+this.threadid,this.dialogText);
        },
        lastpost(){
            return this.posts[this.posts.length-1];
        },
        post_by_postid(postid){
            return this.posts[global.findObject(this.posts,'postid',postid)];
        },
        sendDialogPost(){
            // console.log(this.$refs.dialogEditor.api.getContent());
            if (this.isCommenting){ // || this.dialogText.trim().substr(0,4)=='<p>*'
                let commentText = this.dialogText; // .substr(0,3)+this.dialogText.trim().substr(4,this.dialogText.length);
                this.$socket.emit('dialog_preview', {msg: '', color:''});

                let commentingPostid = this.commentingPostid;
                if (commentingPostid==''){
                    commentingPostid = this.lastpost().postid;
                }

                this.$socket.emit('send_comment', {threadid: this.threadid, msg:commentText, color:this.threadColor,postid:commentingPostid});
                this.setText('');
            }

            if (!this.isBlank(this.dialogText)) {
                this.$socket.emit('send_text', {threadid: this.threadid, msg: this.toBB(this.dialogText.trim(),this.threadColor), color: this.threadColor});
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
        insertComment(data){
            console.log(data.postid);
            this.post_by_postid(data.postid).comments.push(data);
            this.$nextTick(function () {
                dialog_posts_scrollTop() //Вот сюда надо будет добавить условие скроллить или нет
            });
        },
        switchCommenting(isCommenting){
            this.isCommenting = isCommenting;
            this.$socket.emit('diff',{dialog_id:this.threadid, diffs:'', isCommenting:this.isCommenting, color:this.threadColor});
            this.$socket.emit('set_commenting',{isCommenting:this.isCommenting,threadid:this.threadid});
        },

        changeCommenting(){
            this.switchCommenting(!this.isCommenting);
        },
        commentingPost(pst){
            this.commentingPostid = pst.postid;
            this.switchCommenting(true);
        },
        get_msg_html(data, contenteditable) {
            // return "<div class='reply' id='"+data.id+"' contenteditable='"+contenteditable+"' style='color:"+data.color+"'>"+nl2br(data.msg)+"</div>";
        },
        emitChanegedPost(pst,event){
            this.$socket.emit('dialog_change', {msg:this.toBB(pst.pagetext), id:pst.postid, color:pst.color});//, color:event.event.target.style.color

            // this.$socket.emit('dialog_change', {
            //     msg:deltaToBB.deltaToBB(event.quill.getContents()),
            //     id:pst.postid,
            //     color:pst.color});


        },
        editPost(pst,pstkey,event){
            pst.pagetext = event.event.target.innerHTML;
            // pst.pagetext = event.html;
            this.emitChanegedPost(pst, event);
        },
        changePostColor(pst){
            let parser = new DOMParser();
            let newEl = parser.parseFromString(pst.pagetext, "text/xml").firstChild;
            newEl.setAttribute("style", "color:"+pst.color);
            pst.pagetext = newEl.outerHTML;
            this.emitChanegedPost(pst);
        },
        postClick(pst){
            this.curPost = pst.postid;
        },
        focusPost(pst){
            // console.log('activate');
            this.curPost = pst.postid;
            this.delConfirm = false;
        },
        blurPost(pst){
            // if (this.curPost == pst.postid){
            //     this.curPost = 0;
            // }
        },
        delPostStart(pst){
           this.delConfirm = true;
        },
        delPostConfirm(pst){
            this.$socket.emit('del_post',{postid:pst.postid});
        },
        handleClickOutside(){
            this.curPost = 0;
        },

        collapseDialog(){
            this.dialogShow=!this.dialogShow;
        },

        loadThreads(){
            var this_app = this;
            if (this.threads.length==0 || this.curThread.threadid==0){
                axios.get(global.curdomain+'/api/threads/', {withCredentials:true})
                    .then(function (response) {
                        if (this_app.startThread!=0){
                            response.data.threadid = this_app.startThread;
                        };
                        this_app.setThreads(response.data);
                    });
            }
        },

        openThreadSettings(){
            this.isThreadSettings = !this.isThreadSettings;
        },
        setNoteID(){
            this.$socket.emit('set_noteID',{noteID:this.noteID,threadid:this.curThread.threadid});
        }
    },
    mounted(){
        this.openThread = (data) => {
            this.setLastThread(data.threadid);
            if (this.threads.length!=0){
                this.setThreadByID(data.threadid);
            }else {
		        this.startThread = data.threadid;
            }
	    };
        this.$bus.$on("openThread", this.openThread);
    },
    beforeDestroy: function() {
        this.$bus.$off("openThread", this.openThread);
    },
    created(){
        this.loadThreads();
        vueApp = this;
    },
};

</script>

<style>
    .dialog_root{
        width: 100%;
        height: 100%;
    }
</style>
