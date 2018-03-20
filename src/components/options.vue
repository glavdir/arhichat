<template>
<div class="opts_root">
    <div>
        <div class="opts_group">
            <div class='opts_group_tittle'>Подключение</div>
            <div class="option"><my-switch size="sm" color="green" v-model="opts.transport_switch" @input="saveOptions"></my-switch> Автоматическое переключение транспорта</div>
            <div class="option"><my-switch size="sm" color="green" v-model="opts.use_polling" @input="saveOptions"></my-switch> Принудительно использовать polling</div>
            <div class="option"><my-switch size="sm" color="green" v-model="opts.use_kong"  @input="saveOptions"></my-switch> Обезьяна</div>
            <div class="option"><my-switch size="sm" color="green" v-model="opts.show_kong" @input="saveOptions"></my-switch> Показывать интервал ответа от сервера</div>
        </div>
        <div class="opts_group">
            <div class='opts_group_tittle'>Содержимое</div>
            <div class="option"><my-switch size="sm" color="green" v-model="opts.censor" @input="saveOptions">Автоцензор</my-switch> Автоцензор</div>
            <div class="option"><my-switch size="sm" color="green" v-model="opts.show_img" @input="saveOptions">Автоцензор</my-switch> Показывать картинки</div>
        </div>
        <div class="opts_group">
            <div class='opts_group_tittle'>Оформление</div>
            <div class="option"><dropdown :class-name="'styleSelect'" :closeOnClick="true">
                <template slot="btn">{{styleLabel(opts.style)}}</template>
                <template slot="body">
                    <template v-for="(style, key) in styleList" >
                        <label @click="swichStyle(key)">
                            <ul>{{styleLabel(key)}}</ul>
                        </label>
                    </template>
                </template>
            </dropdown></div>
            <div class="option"><input class="opts_font_size" type="number" v-model="local_opts.font_size" @input="saveLocalOptions"> Размер шрифта (локально)</div>
            <div class="option"><input class="opts_font_size" type="number" v-model="local_opts.left_rate" @input="saveLocalOptions"> Ширина левой панели в процентах (локально)</div>
        </div>
        <div class="opts_group">
            <div class='opts_group_tittle'>Чат</div>
            <div class="option">
                <span>Цвет моих сообщений</span>
                <color-select class="bttn" @input="saveOptions" v-model="opts.s_color" :colorlist="[['darkred','#993399','#6600FF','#4444','#4B0082'],
                                                                                                    ['Red','Blue','Teal','RoyalBlue','Navy'],
                                                                                                    ['YellowGreen','Green','Brown','DarkRed','DarkSlateGray'],
                                                                                                    ['Black','Purple','BlueViolet','Indigo','DarkMagenta']]"></color-select>

            </div>
        </div>
    </div>
</div>
</template>


<script>

import color_select from './colorSelect.vue';
import mySwitch from 'vue-switch/switch-2.vue';
import Dropdown from 'bp-vuejs-dropdown';
import global from '../global.js';

var styleList = {
    default:{title:'По умолчанию'},
    dragon:{title:'Дракон'},
    // dragon_old:{title:'Дракон (маленький шрифт)'},
    oceanzero:{title:'Океан'},
};

export default {
    data:function name() {return{
        styleList: styleList,
        // curStyle: global.findObject(styleList, this.$store.state.opts.style)
    }},
    components:{
        'dropdown':Dropdown,
        'my-switch': mySwitch,
        'color-select': color_select,
    },
    methods:{
        styleLabel (option) {
            if (option in this.styleList){
                return this.styleList[option].title;
            }else {
                return "<Стиль не найден>";
            }
        },
        swichStyle(style){
            this.opts.style = style;
            this.saveOptions();
        },
        saveOptions(){
            this.$socket.emit('save_option',this.opts);
        },
        saveLocalOptions(){
            // console.log(this.local_opts);
            localStorage.setItem('local_opts',JSON.stringify(this.local_opts));
            // this.$bus.$emit('panelResize');
            // this.$nextTick(function () {
            //     global.set_chat_users_width();
            // });
        }
    },
    computed:{
        opts:{
            get(){return this.$store.state.opts;},
            set(value){ this.$store.commit("setOpts",value);}
        },
        local_opts:function(){
            return this.$store.state.local_opts;
        }
    },
}
</script>


<style>
    .opts_root{
        padding: 0.5rem;
        position: relative;
        overflow-y: auto;
        height: calc(100%);
        width: 100%;
        box-sizing: border-box;
    }
    .opts_group_tittle{
        font-weight: bold;
        /*padding:0.5rem;*/
    }
    .opts_group{
        margin-bottom: 1rem;
    }

    .opts_font_size{
        width: 3rem;
    }

    .option{
        margin: 0.25rem;
    }

</style>
