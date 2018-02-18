<template>
<div class="characterEdit_root">

    <fieldset>
        <legend>Поиск</legend>
        <div class="flex_container">
            <span class="thickLine">По теме</span>
            <select v-model="currentThread" v-on:change="selectThread" class="flex_element thickLine">
                <option selected value="*" >Все</option>
                <option selected value="" >Квенты</option>
                <option v-for="th in threadList" v-bind:value="th.threadid">{{ th.title }}</option>
            </select>
        </div>
        <div class="flex_container">
            <span class="thickLine">По имени персонажа</span><input type="text" maxlength="64" v-model="charFilter"
                                                                    class="flex_element thickLine"
                placeholder="Просто впиши сюда чать имени">
        </div>

        <select ref="charSelect" v-model="currentChar" v-on:change="selectCharacter" size="5" class="full_width thickLine">
            <!--option selected value="">Новый персонаж</option-->
            <option v-for="ch in filteredCharacterList" v-bind:value="ch.CharId">
                {{ ch.Name }}<template v-if="ch.Thread"> ({{ getThreadNameById(ch.Thread) }})</template>
            </option>
        </select>
    </fieldset>
    <fieldset>
        <legend>Персонаж</legend>
        <div class="flex_container">
            <span class="thickLine">Имя</span><input type="text" maxlength="64" v-model="editData.Name" class="flex_element thickLine"
                placeholder="Новый персонаж">
            <button v-on:click="resetEditData" title="Сброс" class="thickLine">X</button>
        </div>

        <span class="thickLine">Описание</span><br/>
        <textarea v-model="editData.Description" class="full_width thickLine" rows="4"></textarea><br/>
        <span class="thickLine">Стиль текста</span>
        <color-select class="bttn" v-model="editData.TextStyle"
                      :colorlist="[['darkred','#993399','#6600FF','#4444','#4B0082'],
                                ['Red','Blue','Teal','RoyalBlue','Navy'],
                                ['YellowGreen','Green','Brown','DarkRed','DarkSlateGray'],
                                ['Black','Purple','BlueViolet','Indigo','DarkMagenta']]"></color-select>
        <!--input type="text" maxlength="1024" v-model="editData.TextStyle"-->
        <div class="flex_container">
            <span class="thickLine">Тема</span>
            <select v-model="editData.Thread" class="flex_element thickLine">
                <option selected value="" >Квенты</option>
                <option v-for="th in threadList" v-bind:value="th.threadid">{{ th.title }}</option>
            </select>
        </div>
        <div v-if="editData.Author"><span class="thickLine">Автор:</span>
            <span class="display_frame thickLine">{{ editData.AuthorName }}</span></div>
        <button v-on:click="deleteCharacter" id="delete_button" title="отправить персонажа в варп"
        :disabled="!currentChar"  class="thickLine">Удалить</button>
        <button v-on:click="saveChanges" id="save_button" title="Сохранить"  class="thickLine">Сохранить</button>
    </fieldset>
</div>
</template>


<script>
    import global from '../global.js';
    import axios from 'axios';
    import Vue from 'vue';
    import diff_match_patch from 'diff-match-patch'
    import color_select from './colorSelect.vue';


    function editDataDefault(){
         return {
            CharId: null,
            Name: "",
            Description: "",
            TextStyle: null,
            Thread: "",
            Author: null,
            AuthorName: ""
        };
    }

    export default {
        components: {
            'color-select': color_select
        },
        data(){
            return {
                currentThread: "*",
                threadList: [],
                charSearchName: "",
                currentChar: "",
                charList: [],
                charFilter: "",
                editData: editDataDefault()
            }
        },
        computed: {
            filteredCharacterList: function () {
                var filteredCharList = [];
                if(this.charFilter.length == 0)
                    return this.charList;

                for(var c in this.charList)
                {
                    if(this.charList[c].Name.toLowerCase().includes(this.charFilter.toLowerCase()))
                        filteredCharList.push(this.charList[c])
                }
                return filteredCharList;
            }
        },
        created(){
            var this_app = this;
            if (this.threadList.length==0){
                axios.get(global.curdomain+'/api/threads/', {withCredentials:true})
                    .then(function (response) {
                        this_app.setThreadList(response.data);
                        this_app.selectThread();
                    });
            }
        },
        methods: {
            setThreadList: function(data){
                this.threadList = data.threads;
            },
            selectThread: function(){
//                var this_app = this;
//                this.$socket.emit('character_thread_selected', {thread: this.currentThread},
//                                function(data){this_app.setCharacterList(JSON.parse(data)); });
                this.$socket.emit('character_thread_selected', {thread: this.currentThread});
            },

            setCharacterList: function(data){
                var lastCharId = this.currentChar;
                if(data['thread'] == this.currentThread)
                    this.charList = data['characters'];
                if(lastCharId)
                {
                    for(var i in this.charList){
                        if (this.charList[i].CharId == lastCharId) {
                            this.selectCharacter();
                            return;
                        }
                    }
                }
            },

            selectCharacter: function () {
                if(!this.currentChar || this.currentChar.length==0)
                {
                    this.editData = editDataDefault()
                }
                else {
                    var this_app = this;
                    this.$socket.emit('get_character_info', {id: this.currentChar},
                        function (data) {  this_app.setCharacterData(JSON.parse(data)); });
                }
            },
            setCharacterData: function(data){
                if(!data['Thread'])
                    data['Thread'] = ""
                this.editData = data;
            },
            resetEditData: function () {
                this.editData = editDataDefault();
                this.currentChar = null
            },
            saveChanges: function (data) {
                if(this.currentChar)
                {
                    var currentCharText = this.$refs['charSelect'].options[this.$refs['charSelect'].selectedIndex].text;
                    if(!window.confirm('Вы точно хотите изменить персонажа "' + currentCharText + '"?'))
                        return;
                }
                if(this.editData.Name.length == 0 || this.editData.Description.length == 0)
                {
                   alert('Заполните поля "Имя" и "Описание" для сохранения персонажа');
                   return;
                }
                if(!this.editData.Thread)
                    this.editData.Thread = null;
                this.$socket.emit('save_character', {'Character':this.editData,'CurrentThread':this.currentThread} );
            },
            deleteCharacter: function()
            {
                if(!this.currentChar)
                {
                    alert('Такого персонажа не существует. Персонаж не выбран или кто-то его уже удалил пока вы тупили. ' +
                        'Перезагрузите страницу');
                    return;
                }
                var currentCharText = this.$refs['charSelect'].options[this.$refs['charSelect'].selectedIndex].text;
                console.log(currentCharText)
                if(window.confirm('Вы точно хотите удалить персонажа "' + currentCharText + '"?'))
                {
                    if(window.confirm('Если потом передумаете придётся восстанавливать вручную. Точно удалять?'))
                    {
                        var this_app = this
                        this.$socket.emit('delete_character', {'Character':this.currentChar, 'CurrentThread':this.currentThread },
                        function (result) {
                            if (result) {
                                alert('Персонаж "' + currentCharText + '" удалён');
                                this_app.resetEditData();
                            }
                             else
                                 alert('Упс! Что-то пошло не так. Персонаж "' + currentCharText + '" не был удалён');
                         });



                    }
                }
            },
            getThreadNameById(threadId){
                for(var t in this.threadList)
                {
                    if(this.threadList[t].threadid == threadId)
                       return this.threadList[t].title;
                }
                return '*Тема не найдена*';
            }
        },
        sockets:{
             character_list(data){
                this.setCharacterList(JSON.parse(data));
            },
        }
    }
</script>


<style>
    .characterEdit_root{
        padding: 0.5em;
    }

    .thickLine{
         margin: 0.3em 0 0.3em 0;
    }

    /*.characterEdit_root *,.bttn:not {*/
        /*margin: 0.3em 0 0.3em 0;*/
    /*}*/



    .characterEdit_root .flex_container{
        display: -webkit-flex;
        display: flex;
        -webkit-flex-direction: row;
        flex-direction: row;
    }

    .characterEdit_root .flex_element{
        -webkit-flex: auto;
	    flex: auto;
    }

    .characterEdit_root .full_width{
      width: 100%;
    }

    .characterEdit_root span{
        padding: 0 0.5em 0 0;
    }

    .characterEdit_root fieldset{
        border: 1px solid lightgray;
        border-radius: 3px;
    }

</style>
