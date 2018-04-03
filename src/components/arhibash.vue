<template>
    <div class="arhibash_root">
        <div class="arhibash_header header">
            <button class="bttn icon-conteiner" @click="openPrevBash"><icon name="angle-left"></icon></button>
            <button class="bttn icon-conteiner" @click="openNextBash"><icon name="angle-right"></icon></button>
            <span class="flex_splitter">{{postTitle}}</span>
            <button class="bttn icon-conteiner" @click="newBash" title="Новый пост"><icon name="plus"></icon></button>
            <button class="bttn icon-conteiner" @click="saveBash" title="Сохранить"><icon name="floppy-o"></icon></button>
        </div>
        <div class="arhibash_conteiner">
            <medium-editor
                class="arhibash_post"
                :text='pagetext'
                custom-tag='p'
                :options="editorOpts"
                data-placeholder=" "
                @edit="editBash($event)"

            />
        </div>
    </div>
</template>

<script>
    import editor from 'vue2-medium-editor';
    import HTML2BBCode from 'html2bbcode'
    var converter = new HTML2BBCode.HTML2BBCode({weaknewline:false});

    export default {
        data: function () {
            return {
                pagetext:'',
                postid:'',
                time:0,
                editorOpts:{
                    toolbar:{buttons:['bold','italic','underline','strikethrough','removeFormat']},
                    paste:{
                        forcePlainText:true,
                        cleanPastedHTML:true,
                        cleanAttrs:['class', 'style', 'dir', 'text-align'],
                        unwrapTags:['font','br'],
                        cleanTags: ['label', 'meta'],
                        cleanReplacements:[[/\n/g,'<br>']],
                    },
                }
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

                // console.log(converter.feed(this.pagetext).s);

                this.$socket.emit('save_bash',{postid:this.postid, pagetext:converter.feed(this.pagetext).s},function (result) {
                    if (result) {
                        this_app.postid = result.postid;
                        this_app.time = result.time;
                        this_app.flash('Сохранено', 'success', {timeout: 2000});
                    }
                    else
                        this_app.flash('ВНИМАНИЕ! Пост не сохранен!', 'error', {timeout: 10000});

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
                    return this.momentum(this.time*1000).utc().add(this.$store.state.timezoneoffset,'hours').format('DD MMM YYYY');
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
