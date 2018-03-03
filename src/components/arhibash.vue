<template>
    <div class="arhibash_root">
        <div class="arhibash_header header">
            <button class="bttn icon-angle-left" @click="openPrevBash"></button>
            <button class="bttn icon-angle-right" @click="openNextBash"></button>
            <span class="flex_splitter">{{postTitle}}</span>
            <button class="bttn" @click="newBash">Новый пост</button>
            <button class="bttn" @click="saveBash">Сохранить</button>
        </div>
        <div class="arhibash_conteiner">
            <medium-editor
                class="arhibash_post"
                :text='pagetext'
                custom-tag='div'
                :options="{toolbar:{buttons:['bold','italic','underline','strikethrough']}}"
                data-placeholder=" "
                @edit="editBash($event)"
            />
        </div>
    </div>
</template>

<script>
    import editor from 'vue2-medium-editor';
    // import Vue from 'vue'
    import htmltobb from "../htmltobb";
    // import global from "../global";



    export default {
        data: function () {
            return {
                pagetext:'',
                postid:'',
                time:0
            }
        },
        methods: {
            openBash(params){
                let this_app = this;
                this.$socket.emit('open_bash',params,function (data) {
                    this_app.postid = data.postid;
                    this_app.pagetext = data.pagetext;
                    this_app.time = data.time;
                });
            },
            openPrevBash(){
                this.openBash({postid:this.postid, direction:'prev'});
            },
            openNextBash(){
                this.openBash({postid:this.postid, direction:'next'});
            },
            openLastBash(){
                this.openBash({postid:0, direction:'last'});
            },
            saveBash(event){
                let this_app = this;
                this.$socket.emit('save_bash',{postid:this.postid, pagetext:htmltobb(this.pagetext)},function (result) {
                    if (result) {
                        this_app.postid = result.postid;
                        console.log(this_app.flash('Сохранено', 'success', {timeout: 2000}));
                    }
                    else
                        console.log(this_app.flash('ВНИМАНИЕ! Пост не сохранен!', 'error', {timeout: 10000}));

                });
            },
            newBash(){
                this.postid = '';
                this.pagetext = '';
                this.time = 0;
            },
            editBash(event){
                this.pagetext = event.event.target.innerHTML;
            }
        },
        computed:{
            postTitle(){
                if (this.time==0){
                    return '* новый пост';
                }else{
                    return this.momentum(this.time*1000).utc().add(this.$store.state.timezoneoffset,'hours').subtract(0, 'days').calendar();
                }
            }
        },
        components: {
            'medium-editor':editor
        },
        created(){
            this.openLastBash();
        }

    }
</script>

<style scoped>

</style>
