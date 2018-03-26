<template>
    <div class="characterEdit_root">

        <fieldset class="frame">
            <legend>Поиск</legend>
            <div class="flex_container thickLine">
                <span class="space_after v_center">Имя</span>
                <input type="text" maxlength="64" v-model="charFilter"
                       class="flex_element input_field"
                       placeholder="Имя или его часть">
            </div>
            <div class="flex_container thickLine">
                <span class="space_after v_center">Тэги</span>
                <tag-select
                    v-model="tagsFilter"
                    :existing-tags="allTagsDict"
                    :typeahead="true"
                    placeholder="Тэги"
                    class="flex_container flex_element"
                ></tag-select>
            </div>
            <select ref="charSelect" v-model="currentChar" @change="selectCharacter" size="5"
                    class="full_width thickLine">
                <option v-for="ch in filteredCharacters" v-bind:value="ch.id">{{ ch.name }}</option>
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
                <tag-select
                    v-model="editData.newTags"
                    :old-tags="editData.tags"
                    :existing-tags="allTagsDict"
                    :typeahead="true"
                    placeholder="Тэги"
                    class="flex_container flex_element"
                ></tag-select>
            </div>
            <div v-if="editData.author" class="thickLine">
                <span>Автор:</span>
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
    import tag_select from '@voerro/vue-tagsinput'


    Vue.config.keyCodes.backspace = 8;

    function editDataDefault() {
        return {
            id: null,
            name: "",
            description: "",
            author: null,
            author_name: "",
            tags: ['default'],
            newTags: []
        };
    }

    export default {
        components: {
            'tags-input': tags_input,
            'tag-select': tag_select
        },
        data() {
            return {
                currentChar: "",
                charList: [],
                charFilter: "",
                tagsFilter: null,
                tagPattern: "[\\s0-9a-zA-Zа-яА-Я_]+",
                editData: editDataDefault(),
                allTags: [],
                allTagsDict: {}
            }
        },
        created() {
            var this_app = this;
            this.$socket.emit('find_characters');
            this.$socket.emit('get_tags');
        },
        computed: {
            filteredCharacters: function () {
                var nameFilter = this.charFilter.trim()
                var filterName = nameFilter.length > 0
                var filterTags = this.tagsFilter

                if (!filterName && !filterTags) {
                    return this.charList;
                }

                var filtered = []
                for (var c in this.charList) {
                    var character = this.charList[c]
                    if (filterName && character.name.toLowerCase().includes(nameFilter.toLowerCase())) {
                        if (!filtered.includes(character))
                            filtered.push(character)
                        continue
                    }
                    if (filterTags) {
                        var suits = true

                        for (var i in this.tagsFilter) {
                            if (!character.tags.includes(this.tagsFilter[i])) {
                                suits = false;
                                break;
                            }
                        }
                        if (suits && !filtered.includes(character))
                            filtered.push(character)
                    }
                }
                return filtered;
            }
        },

        methods: {
            remove_empty_elements: function (stringlist) {
                var newList = []
                for (var s in stringlist) {
                    if (stringlist[s] != '')
                        newList.push(stringlist[s])
                }
                return newList
            },
            find_characters: function () {
                var filters = {
                    name: this.charFilter,
                    tags: this.remove_empty_elements(this.tagsFilter)
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
                this.editData.tags.push('sometag')
            },
            resetEditData: function () {
                this.editData = editDataDefault();
                this.currentChar = null
            },
            saveChanges: function (data) {
                let this_app = this;
                if (this.currentChar) {
                    var currentCharText = this.$refs['charSelect'].options[this.$refs['charSelect'].selectedIndex].text;
                    if (!window.confirm('Вы точно хотите изменить персонажа "' + currentCharText + '"?'))
                        return;
                }
                if (this.editData.name.length == 0 || this.editData.description.length == 0) {
//                    alert('Заполните поля "Имя" и "Описание" для сохранения персонажа');
                    this.flash('Заполните поля "Имя" и "Описание" для сохранения персонажа', 'error', {timeout: 2000})
                    return;

                }
                this.editData.tags = this.remove_empty_elements(this.editData.tags)
                var name = this.editData.name
                this.$socket.emit('save_character', {'Character': this.editData}, function (result) {

                    if (result) {
//                        alert('Персонаж "' + name + '" успешно сохранен');
                        this_app.flash('Персонаж "' + name + '" успешно сохранен', 'success', {timeout: 2000})
                        this_app.find_characters();
                        this_app.setCharacterData(JSON.parse(result));
                    }
                    else
                        this_app.flash('Упс! Не получилось создать персонажа "' + name + '"', 'error', {timeout: 2000})
//                        alert('Упс! Не получилось создать персонажа "' + name + '"');

                })
            },
            deleteCharacter: function () {
                let this_app = this;
                if (!this.currentChar) {
//                    alert('Такого персонажа не существует. Персонаж не выбран или кто-то его уже удалил пока вы тупили. ' +
//                        'Перезагрузите страницу');
                    this.flash('Такого персонажа не существует. Персонаж не выбран или кто-то его уже удалил пока вы тупили. ' +
                        'Перезагрузите страницу', 'error', {timeout: 2000})
                    return;
                }
                var currentCharText = this.$refs['charSelect'].options[this.$refs['charSelect'].selectedIndex].text;
                console.log(currentCharText)
                if (window.confirm('Вы точно хотите удалить персонажа "' + currentCharText + '"?')) {
                    if (window.confirm('Если потом передумаете придётся восстанавливать вручную. Точно удалять?')) {
                        this.$socket.emit('delete_character', {'Character': this.currentChar},
                            function (result) {
                                console.log(result)
                                if (result) {
                                    alert('Персонаж "' + currentCharText + '" удалён');
                                    this_app.resetEditData();
                                    this_app.find_characters();
                                }
                                else
                                    this_app.flash('Упс! Что-то пошло не так. Персонаж "' + currentCharText + '" не был удалён',
                                        'error', {timeout: 2000})
//                                    alert('Упс! Что-то пошло не так. Персонаж "' + currentCharText + '" не был удалён');
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
                for (var tag in this.allTags) {
                    this.allTagsDict[this.allTags[tag]] = this.allTags[tag];
                }
            }
        }
    }
</script>

<style scoped>


    .characterEdit_root {
        padding: 0.5em;
    }

    .flex_container {
        display: -webkit-flex;
        display: flex;
        -webkit-flex-direction: row;
        flex-direction: row;
        flex-wrap: wrap;
    }

    .flex_element {
        flex-grow: 1;
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

    .v_center {
        margin: auto;
    }


</style>

<style>

    .characterEdit_root .form-control {
        padding: 0.1rem 0.2rem;
        width: inherit;
    }

    .characterEdit_root .badge-light {
        font-size: 100%;
    }

    .characterEdit_root .tags-input {
        flex-grow: 2;
    }

    .characterEdit_root .input_field {
        border: 1px solid #ced4da;
        border-radius: 0.25rem;
        padding: 0.1rem 0.2rem;
    }

    /* .characterEdit_root input[type="text"] {
         padding: 0 0.1em;
     }




 /*
     .tags-input{
         display: flex;
         flex-wrap: wrap;
         align-items: center;
     }
     .tags-input .badge{
         background-color: #f0f0f0;
         border-radius: 6px;
         padding: 0.1rem 0.2rem;
     }*/


</style>
