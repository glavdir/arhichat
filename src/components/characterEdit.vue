<template>
    <div class="characterEdit_root">

        <fieldset class="frame">
            <legend>Поиск</legend>
            <div class="flex_container thickLine">
                <span class="space_after v_center">Имя</span><input type="text" maxlength="64" v-model="charFilter"
                                                                     class="flex_element input_field v_center"
                                                                     placeholder="Имя или его начало">
            </div>
            <div class="flex_container thickLine">
                <span class="space_after v_center">Тэги</span>
                <tags-input class="flex_element v_center"
                            :fullTagList="allTags"
                            v-model="tagsFilter"
                            maxlength="64"
                            placeholder="Тэги через пробел"/>
            </div>
            <div class="flex_container thickLine">
                <div class="flex_container">
                    <input type="checkbox" v-model="quentasOnly" class="v_center">
                    <div class=" space_after"></div>
                    <span class="v_center">Только квенты</span>
                </div>
                <div class="flex_element"></div>
                <button @click="find_characters">Найти</button>
            </div>
            <select ref="charSelect" v-model="currentChar" @change="selectCharacter" size="5"
                    class="full_width thickLine">
                <option v-for="ch in charList" v-bind:value="ch.id">{{ ch.name }}</option>
            </select>
        </fieldset>
        <fieldset class="frame">
            <legend>Персонаж</legend>
            <div class="flex_container thickLine">
                <span class="space_after v_center">Имя</span>
                <input type="text" maxlength="64"
                       v-model="editData.name"
                       class="flex_element input_field"
                       placeholder="Мне нужно ИМЯ!">
            </div>

            <span class="thickLine v_center">Описание</span><br/>
            <div class="flex_container">
                <textarea v-model="editData.description" class="full_width thickLine" rows="4"></textarea>
            </div>
            <div id="character_tags_container" class="flex_container thickLine" @keydown.esc="showTagSelector(false)">
                <span class=" space_after v_center">Тэги</span>
                <tags-input class="flex_element v_center"
                            :fullTagList="allTags"
                            v-model="editData.tags"
                            maxlength="64"
                            placeholder="Тэги через пробел"/>
            </div>
            <div v-if="editData.author" class="thickLine">
                <span >Автор:</span>
                <span class="display_frame ">{{ editData.author_name }}</span>
            </div>
            <div class="flex_container thickLine">
                <button @click="resetEditData" title="Сбросить редактирование">Новый</button>
                <div class="flex_element"></div>
                <button @click="deleteCharacter" id="delete_button" title="Отправить персонажа в варп"
                        :disabled="!currentChar">Удалить
                </button>
                <button @click="saveChanges" id="save_button" title="Сохранить">Сохранить
                </button>

            </div>
        </fieldset>
    </div>
</template>


<script>
    import global from '../global.js';
    import Vue from 'vue';
    import diff_match_patch from 'diff-match-patch'
    import tags_input from './tagsInput.vue'

    function editDataDefault() {
        return {
            id: null,
            name: "",
            description: "",
            author: null,
            author_name: "",
            tags: []
        };
    }

    export default {
        components: {
            'tags-input': tags_input
        },
        data() {
            return {
                currentChar: "",
                charList: [],
                charFilter: "",
                tagsFilter: [],
                tagPattern: "[\\s0-9a-zA-Zа-яА-Я_]+",
                editData: editDataDefault(),
                allTags: [],
                quentasOnly: false
            }
        },
        created() {
            var this_app = this;
            this.$socket.emit('get_tags');
        },
        methods: {
            remove_empty_elements: function (stringlist) {
                var pos = 0
                while (pos < stringlist.length) {
                    if (stringlist[pos] == '')
                        stringlist.splice(pos, 1)
                    else
                        pos += 1
                }
                return stringlist
            },
            find_characters: function () {
                var filters = {
                    name: this.charFilter,
                    tags: this.remove_empty_elements(this.tagsFilter),
                    quentasOnly: this.quentasOnly
                }
                this.$socket.emit('find_characters', filters);
            },
            setCharacterList: function (data) {
                var lastCharId = this.currentChar;
                this.charList = data;
                if (lastCharId) {
                    for (var i in this.charList) {
                        if (this.charList[i].id == lastCharId) {
                            this.selectCharacter();
                            return;
                        }
                    }
                }
            },

            selectCharacter: function () {
                if (!this.currentChar || this.currentChar.length == 0) {
                    this.editData = editDataDefault()
                }
                else {
                    var this_app = this;
                    this.$socket.emit('get_character_info', {id: this.currentChar},
                        function (data) {
                            this_app.setCharacterData(JSON.parse(data));
                        });
                }
            },
            setCharacterData: function (data) {
                this.editData = data;
            },
            resetEditData: function () {
                this.editData = editDataDefault();
                this.currentChar = null
            },
            saveChanges: function (data) {
                if (this.currentChar) {
                    var currentCharText = this.$refs['charSelect'].options[this.$refs['charSelect'].selectedIndex].text;
                    if (!window.confirm('Вы точно хотите изменить персонажа "' + currentCharText + '"?'))
                        return;
                }
                if (this.editData.name.length == 0 || this.editData.description.length == 0) {
                    alert('Заполните поля "Имя" и "Описание" для сохранения персонажа');
                    return;
                }
                this.editData.tags = this.remove_empty_elements(this.editData.tags)
                var name = this.editData.name
                var this_app = this;
                this.$socket.emit('save_character', {'Character': this.editData}, function (result) {

                                if (result) {
                                    alert('Персонаж "' + name + '" успешно сохранен');
                                    this_app.find_characters();
                                    this_app.setCharacterData(JSON.parse(result));
                                }
                                else
                                    alert('Упс! Не получилось создать персонажа "' + name + '"');
                            })
            },
            deleteCharacter: function () {
                if (!this.currentChar) {
                    alert('Такого персонажа не существует. Персонаж не выбран или кто-то его уже удалил пока вы тупили. ' +
                        'Перезагрузите страницу');
                    return;
                }
                var currentCharText = this.$refs['charSelect'].options[this.$refs['charSelect'].selectedIndex].text;
                console.log(currentCharText)
                if (window.confirm('Вы точно хотите удалить персонажа "' + currentCharText + '"?')) {
                    if (window.confirm('Если потом передумаете придётся восстанавливать вручную. Точно удалять?')) {
                        var this_app = this
                        this.$socket.emit('delete_character', {'Character': this.currentChar},
                            function (result) {
                            console.log(result)
                                if (result) {
                                    alert('Персонаж "' + currentCharText + '" удалён');
                                    this_app.resetEditData();
                                    this_app.find_characters();
                                }
                                else
                                    alert('Упс! Что-то пошло не так. Персонаж "' + currentCharText + '" не был удалён');
                            });
                    }
                }
            }
        },
        sockets: {
            character_list(data) {
                this.setCharacterList(JSON.parse(data))
            },
            character_tags(data) {
                this.allTags = JSON.parse(data)
            }
        }
    }
</script>

<style scoped>
    .characterEdit_root {
        padding: 0.5em;
    }

    input_field {
        border: 1px solid gray;
        padding: 0 0.1em;
    }

    .flex_container {
        display: -webkit-flex;
        display: flex;
        -webkit-flex-direction: row;
        flex-direction: row;
        flex-wrap: wrap;
    }

    .flex_element {
        flex-grow: 2;
    }

    .full_width {
        width: 100%;
    }

    .space_after {
        padding-right: 0.5rem;
    }

    .frame {
        border: 1px solid lightgray;
        border-radius: 3px;
    }

    .thickLine {
        margin: 0.3em 0 0.3em 0;
    }

    .v_center
    {
        margin: auto;
    }

</style>

<style>
    .characterEdit_root input[type="text"]{
        padding: 0 0.1em;
    }
</style>
