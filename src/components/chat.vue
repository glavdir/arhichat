<template>
<div class="chat_root">
    <div class="chat_header header ">
        <div class="chat_users">
            <!--:style="'width:'+users_width+'px'"-->
            <div class="activeusers">
                <div v-for="user in $store.state.users" :key="user.userid"
                             v-bind="{'data-pmid': user.userid}"
                             v-bind:class="{tabUser:true, tabActive:user.userid==curpmid, unread: user.unread}"
                             v-html="user.userlook"
                             @click="tabOnClick(user.userid)">

                </div>
            </div>
        </div>
    </div>
    <div class="chat_main">
        <div class="channels" @click="shoutClick($event)">
            <div v-for="channel in channels" :key="channel.name" v-bind="{ id: channel.name, 'data-pmid': channel.pmid }">
                <template v-if="channel.name == curchannel">
                        <div v-for="message in channel.messages" :key="message.sid"
                        class="msg"
                        v-bind="{'data-sid': message.sid, key:message.sid}" @dblclick="editStart">
                            <chat-shout v-show="curEditSid!=message.sid" class="shout" v-bind="{'data-sid': message.sid}"
                                            :sid="message.sid"
                                            :me ="message.me"
                                            :s_user ="message.s_user"
                                            :user ="message.user"
                                            :time ="message.time"
                                            :color ="message.color"
                                            :msg ="message.msg"
                                            v-on:tabOnClick="tabOnClick"
                                ></chat-shout>
                        <div v-if="curEditSid==message.sid" class="edit-div">
                            <input v-focus="curEditSid!=0" ref="chat_edit_text" class="edit-input chat_edit_text" placeholder="Редактирование сообщения" v-model="curEditText" @keydown.enter="editConfirm">
                            <button class="bttn icon-ok chat_edit_OK" title="OK" @click="editConfirm"></button>
                            <button class="bttn icon-trash chat_edit_Delete" title="Удалить" @click="editDelete"></button>
                            <button class="bttn icon-cancel chat_edit_Cancel" title="Отмена" @click="editFinish"></button>
                        </div>
                    </div>
                    <button class="addMessages" @click="loadMessages(channel)">Загрузить еще...</button>
                </template>
            </div>
        </div>
    </div>
    <div class="chat_footer">
        <div class="chat_senddiv">
            <input  class="chat_text edit-input" placeholder="Сообщения для бога сообщений"  v-model="chat_text" @keydown.enter="sendMessage">
            <button class="chat_send bttn icon-ok" title="Отправить" @click="sendMessage"></button>
        </div>
    </div>
</div>
</template>

<script>
    import shout from './shout.vue';
    import Vue from 'vue';
    import global from '../global.js';

    Vue.directive('focus', {
        inserted: function (el, binding, vnode) {
            Vue.nextTick(function () {
                el.focus()
            })
        }
    });

    // var chat_app;

    export default {
        data: function() {return{
            channels: {
                arhichat: {
                    name: 'arhichat',
                    messages: [],
                    pmid: -1
                },
                pmchat: {
                    name: 'pmchat',
                    messages: [],
                    pmid: 0
                }
            },
            curpmid: -1,
            curchannel: 'arhichat',
            chat_text: '',
            curEditSid: 0,
            curEditText: '',
            rootID: 'chat'+Date.now()
        }},
        sockets: {
            messages(data) {
                this.setMessages(-1,data.msgs);
                this.setUnreads(data.unreads);
            },
            open_private(data) {
                this.setMessages(-1,data.msgs);
                this.setUnreads(data.unreads);
            },
            activeusers: function(data) {
                this.$store.commit('setUsers',data.slice());
                // this.$nextTick(function () {
                //     global.set_chat_users_width();
                // });
            },
            one_message:function(data) {
                if (data.action=='new') {
                    this.addMessage(data.message);
                }else if(data.action=='delete' || data.action=='edit')
                {
                    this.updMessage(data.message,data.action);
                }
            }
        },
        methods: {
            setPmid (pmid) {
                this.curpmid = pmid;
                this.curchannel = (pmid == -1) ? 'arhichat' : 'pmchat';

            },
            setUnreads (unreads) {
                this.$store.commit('setUnreads',unreads);
            },
            addUnread (userid) {
                this.$store.commit('addUnread',userid);
            },
            delUnread (userid) {
                this.$store.commit('delUnread',userid);
            },
            getChannel (pmid) {
                if (pmid == -1) {
                    return this.channels.arhichat;
                } else {
                    return this.channels.pmchat;
                }
            },
            setMessages (pmid, messages) {
                this.getChannel(pmid).messages = messages.slice().reverse();
            },
            addMessage (msgData) {
                var pmlinkid = (msgData.pmid==this.$store.state.curuserid) ? msgData.s_user : msgData.pmid;

                //В главный чат добавляем сообщение всегда, в ЛС только если просматривается канал с юзером
                if (pmlinkid==-1 || pmlinkid==this.curpmid){
                    this.getChannel(msgData.pmid).messages.unshift(msgData);
                }

                //Выводим метку непрочитанного если вклака не равна текущей и это не личка, отправленная самим собой из другого окна браузера
                if ((msgData.pmid != pmlinkid||pmlinkid==-1) && pmlinkid != this.curpmid) {
                    this.addUnread(pmlinkid);
                }

                //Если это ЛС и вкладка юзера открыта, убираем оповещение
                if (this.curpmid!= -1 && pmlinkid == this.curpmid){
                    this.$socket.emit('read_private', pmlinkid);
                }
            },
            updMessage (msgData, action) {
                var chn = this.getChannel(msgData.pmid);
                var messages = chn.messages.slice();
                var ind = global.findObject(messages, 'sid', msgData.sid);
                if (action == 'delete') {
                    messages.splice(ind, 1);
                } else {
                    messages[ind] = msgData;
                }
                chn.messages = messages;
            },
            tabOnClick (userid) {
                if (userid != -1) {
                    var this_app = this;
                    this.$socket.emit('open_private', {pmid: userid}, function (data) {
                        this_app.setMessages(userid, JSON.parse(data).msgs);
                        this_app.setPmid(userid);
                    });
                } else {
                    this.setPmid(userid);
                }
                this.delUnread(userid);
            },
            applyTextEdit (text) {
                this.text = text
            },
            sendMessage () {
                if (this.chat_text!=''){
                    var this_app = this;
                    this.$socket.emit('chat_text', {msg: this.chat_text, pmid:this.curpmid},function(callbacks){
                        if (callbacks){
                            callbacks = JSON.parse(callbacks);
                            callbacks.forEach(function(callback, i){
                                if (callback.call =='open_private'){
                                    this_app.tabOnClick(callback.param.pmid);
                                }
                            })
                        }
                    });
                    this.chat_text = '';
                }
            },
            editStart (event) {
                var sid = event.currentTarget.dataset.sid;
                var this_app = this;
                this.$socket.emit('edit_message', {sid: sid}, function (cbk) {
                    if (cbk){
                        this_app.curEditSid = sid;
                        this_app.curEditText = cbk.shout.msg;
                    }
                });
            },
            editConfirm () {
                this.$socket.emit('edit_commit', {msg: this.curEditText, sid:this.curEditSid});
                this.editFinish();
            },
            editDelete () {
                this.$socket.emit('edit_delete', {sid:this.curEditSid});
                this.editFinish();
            },
            editFinish () {
                this.curEditSid = '';
                this.curEditText = '';
            },
            shoutClick(event){
                if (event.target.className=='msglink'){
                   this.$store.commit('setPanel',{panel:'right',  param:'Dialog'});
                    var threadid = event.target.dataset.dialog_id;
                    this.$nextTick(function () {
                        this.$bus.$emit('openThread', {threadid:threadid,panel:'right'});
                    });
                }
            },
            loadMessages(channel){
                var this_app = this;
                if (channel.messages.length>0){
                    this.$socket.emit('load_messages', {pmid:this.curpmid, sid:channel.messages[channel.messages.length-1].sid}, function (cbk) {
                        if (cbk){
                            this_app.channels[channel.name].messages = channel.messages.concat(JSON.parse(cbk).msgs.reverse());
                        }
                    });
                }
            }
        },
        computed:{
        },
        mounted(){
            // global.set_chat_users_width();
            // this.$bus.$on("panelResize", function(){
            //     setTimeout(set_chat_users_width,500)
            // });
        },
        beforeDestroy: function() {
            // this.$bus.$off("panelResize");
        },
        created(){
            this.$socket.emit('get_activeusers');
            var this_app = this;
            this.$socket.emit('get_messages',{pmid:-1}, function (data) {
                this_app.setMessages(-1, JSON.parse(data).msgs);
            });
        },
        components:{
            'chat-shout':shout,
        }
    }
</script>

<style>
.chat_header  {
  display:flex
}
</style>
