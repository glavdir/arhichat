<script>
    import ClickOutside from 'onclick-outside';

    export default {
        model: {
            prop: 'outTags',
            event: 'input'
        },
        props: {
            outTags: Array,
            fullTagList: Array
        },
        components:{
            ClickOutside
        },
        data: function () {
            return {
//                inputText: '',
                listVisible: false,
                listFilter: ''
            }
        },
        computed: {
            tags_filtered: function () {
                if (this.inputText == 0) {
                    return this.fullTagList
                }
                var tags = []
                for (var t in this.fullTagList) {

                    if (this.fullTagList[t].includes(this.listFilter))
                        tags.push(this.fullTagList[t])
                }
                return tags
            },
            inputText: {
                get: function () {
                    return this.outTags.join(' ')
                },
                set: function (tags_string) {
                    var tags = this.validate_string(tags_string).split(' ')
                    this.$emit('input', tags)
                }
            }
        },
        methods: {
            setSelectorVisible: function (show) {
                this.listVisible = show
                if (!show)
                    this.listFilter = ""
            },
            validate_string: function (tags_string) {
                var str = tags_string.toLowerCase().replace(/\s+/g, ' ').replace(/[^\s0-9a-zA-Zа-яА-Я_]+/, '')
                return str
            },
            addTagToOut(tag) {
                this.setSelectorVisible(false)
                if (!this.outTags.includes(tag))
                    this.outTags.push(tag)
            },
            handleClickOutside(e) {
                this.setSelectorVisible(false)
            }
        }
    }
</script>

<template>
    <click-outside :handler="handleClickOutside">
        <div @keydown.esc="setSelectorVisible(false)" class="tags">
            <input type="text" ref="tags_input" placeholder="Тэги через пробел"
                   @keydown.down="setSelectorVisible(true)" class="tags_input" v-model="inputText">

            <button @click="setSelectorVisible(!listVisible)" class="tags_select_button"
                    title="Добавить тэг из списка существующих.
Открывается нажатием ↓ из строки поиска">+
            </button>

            <div ref="tag_list" class="tags_list_frame" v-if="listVisible">
                <input type="text" v-model="listFilter" placeholder=" Поиск" class="tags_select_search">
                <ul>
                    <li v-for="tag in tags_filtered" @click="addTagToOut(tag)" class="tags_select_li">{{ tag }}</li>
                </ul>
            </div>
        </div>
    </click-outside>
</template>


<style scoped>

    .tags {
        position: relative;
        display: flex;
        flex-grow: 2;
        border: 1px solid lightgray;
    }

    .tags_input {
        border: none;
        flex-grow: 2;
    }

    .tags_select_button {
        cursor: pointer;
        border: none;
        border-left: 1px solid #fafafa;
        background: #f8f8f8;
        flex-grow: 0;
    }

     .tags_select_button:hover {
         background-color: white;
     }

    .tags_list_frame {
        position: absolute;
        overflow: auto;
        max-height: 6rem;
        top: calc(100% + 2px);
        background: white;
        border-radius: 0;
        right: 0;
        z-index: 100;
        padding: 0.2em;
        border: 1px solid gray;
        box-shadow: 3px 3px 5px 0 rgba(0, 0, 0, 0.2);
    }

    .tags_list_frame ul {
        margin: 0.3em 0;
    }

    .tags_list_frame li {
        padding: 0 0.3em 0 0.2em;
        cursor: pointer;
    }

    .tags_list_frame li:hover {
        background-color: #CFE7F0;
    }

    .tags_select_search
    {
        border: none;
        border-bottom: 1px solid lightgray;
    }




</style>
