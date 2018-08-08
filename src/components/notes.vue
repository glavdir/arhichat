<template>
    <div class="notes_root">
        <div class="notes_header">
            <div class="notes_tabs_actions">
                <button class="bttn icon-conteiner" @click="delTab" title="Удалить заметку"><icon name="trash"></icon></button>
                <button class="bttn icon-conteiner" @click="addTab" title="Добавить заметку"><icon name="plus"></icon></button>
            </div>
            <div class="note_bar">
                <div class="note_title">
                    <div v-if="!isEditTittle" @dblclick.prevent="tabEdit">{{noteTitle}}</div>
                    <div v-if="isEditTittle" @keydown.enter="editConfirm"><input v-focus="isEditTittle" class="editNoteTitle" v-model="noteTitle"/></div>
                </div>
                <div class="note_opts">
                    <button @click="lockNote" class="bttn icon-conteiner">
                        <icon :name=" !notePrivate ? 'unlock' : 'lock'"></icon>
                    </button>
                </div>
            </div>
        </div>
        <div class="notes_wrapper">
            <div class="notes_tabs_nav">
                <div class="notes_tabs">
                    <div
                         v-for="(tab, index) in tabs"
                         :key="tab.id"
                         :data-noteid="tab.id"
                         :class="[tab.id === curTab ? 'notes_tab notes_tab_active' : 'notes_tab']"
                         @click="tabActivate(tab)"
                         v-dragging="{ item: tab, list: tabs, group: 'notes' }"
                    >
                        <div class="notes_tab_label" v-if = '!tab.editing'>{{tabTitle(tab)}}</div>
                        <!--<div class="notes_tab_label notes_tab_editing" v-focus="tab.editing" v-if = 'tab.editing' contenteditable="true" @blur="tabEndChange(tab,$event)" @keydown.enter.prevent="tabEndChange(tab,$event)">{{tab.title}}</div>-->
                    </div>
                </div>
            </div>
            <!--:options="{toolbar: false}"-->
            <div class="note_text">
                <medium-editor
                    class="note_editor"
                    :text='noteText'
                    custom-tag='div'
                    :options="editorOpts"
                    data-placeholder=" "
                    v-on:edit='editNote($event)'/>
            </div>

        </div>

    </div>
</template>

<script>
    import 'vue-awesome/icons/lock'
    import 'vue-awesome/icons/unlock'

    import mySwitch from 'vue-switch/switch-2.vue';

    import diff_match_patch from 'diff-match-patch'
    var dmp = new diff_match_patch.diff_match_patch();

    import editor from '../MediumEditor.js';

    import Vue from 'vue'
    import VueDND from 'awe-dnd'
    import global from "../global";
    Vue.use(VueDND);

    export default {
        data: function () {
            return {
                tabs: [],
                curTab:'',
                noteText:'',
                noteTitle:'',
                notePrivate:false,
                isEditTittle:false,
                editorOpts:{
                    toolbar:{
                        buttons:['bold','italic','underline','strikethrough','removeFormat'],
                        diffTop: (this.$isMobile.any) ? -50 : -10
                    },
                    paste:{
                        forcePlainText:false,
                        cleanPastedHTML:true,
                        cleanAttrs:['class', 'style', 'dir', 'text-align'],
                        unwrapTags:['font']
                    },
                }
            }
        },
        methods: {
            getTab(tabID) {
                return this.tabs[global.findObject(this.tabs,'id',tabID)];
            },
            addTab() {
                var this_app = this;
                this.$socket.emit('add_note','',function (data) {
                    // console.log(data);
                    var newTab = {id:data.id,title:data.title,editing:false};
                    // this_app.$set(this_app.tabs,'note_'+newTab.id, newTab);
                    this_app.tabs.unshift(newTab);
                    this_app.tabActivate(newTab);
                });
            },
            delTab(){
                if(this.curTab!='' && window.confirm('Удалить заметку?'))
                {
                    var this_app = this;
                    this.$socket.emit('del_note', {id:this.curTab},
                    function (result) {
                        if (result) {
                            var index = global.findObject(this_app.tabs,'id',this_app.curTab);
                            this_app.tabs.splice(index,1);
                            if (this_app.tabs.length>0){
                                this_app.tabActivate(this_app.tabs[0]);
                            }else{
                                this_app.curTab='';
                                this_app.noteText='';
                            }
                        }
                     });
                }
            },
            tabActivate(tab){
                var this_app = this;
                this.$socket.emit('open_note',{id:tab.id},function (data) {
                    this_app.curTab = data.id;
                    this_app.noteText = data.note;
                    this_app.noteTitle = tab.title;
                    this_app.notePrivate = tab.private;
                });
            },
            tabEdit(){
                this.isEditTittle = true;
            },
            editConfirm(){
                this.getTab(this.curTab).title = this.noteTitle;
                this.isEditTittle = false;
                this.$socket.emit('rename_note',{id:this.curTab,title:this.noteTitle});
            },
            tabTitle:function (tab) {
                return (tab.title=='' || !tab.title)?'<заметка>':tab.title;
            },
            editNote(event){
                var newText = event.event.target.innerHTML;
                var oldText = this.noteText;
                this.noteText = newText;

                var diffs = dmp.patch_make(oldText,newText);
                this.$socket.emit('note_diff',{id:this.curTab, diffs:dmp.patch_toText(diffs)});
            },
            saveNotesOrder(){
                var order = [];
                for (var ind in this.tabs){
                    order.push(''+this.tabs[ind].id);
                }
                this.$socket.emit('notes_order',{order:order});
            },
            lockNote(){
                var this_app = this;
                this.$socket.emit('reprivate_note',{id:this.curTab},function (data) {
                    this_app.notePrivate = data;
                });
            }
        },
        computed:{
            content:function () {
                return this.tabs['note_'+this.curTab];
            },

        },
        components: {
            'medium-editor':editor,
            'my-switch': mySwitch
        },
        mounted(){
            this.$dragging.$on('dragend', () => {
                this.saveNotesOrder();
            })
        },
        created(){
            var this_app = this;
            this.$socket.emit('get_notes','',function (data) {
                this_app.tabs = data.notes;
                var keys = Object.keys(this_app.tabs);
                if (keys.length>0){
                   this_app.tabActivate(this_app.tabs[keys[0]]);
                }
            });
        }

    }
</script>

<style scoped>

</style>
