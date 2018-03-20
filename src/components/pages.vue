<template>
    <div class="page_nav_block">
        <div class="page_nav icon-conteiner" @click="firstPage"><icon name="angle-double-left"></icon></div>
        <div class="page_nav icon-conteiner" @click="decPage"><icon name="angle-left"></icon></div>
        <input class="page_nav_input"
            type="text" min="1" :max="pageCount"
            :placeholder="''+curPage+' из '+pageCount"
            v-model="dispPage"
            @change="dispPageChange"
            @focus="doFocus"
            @blur="doBlur"
        >
        <div class="page_nav icon-conteiner" @click="incPage"><icon name="angle-right"></icon></div>
        <div class="page_nav icon-conteiner" @click="lastPage"><icon name="angle-double-right"></icon></div>
    </div>
</template>

<script>
    export default {
        name:"pages",
        props:['pageCount','value'],
        data:function(){return {
            curPage: this.value,
            dispPage: ''
        }},
        methods:{
            incPage(){
                if (this.curPage<this.pageCount){
                    this.curPage++;
                    this.$emit('input',this.curPage);
                }
            },
            decPage(){
                if (this.curPage>1){
                    this.curPage--;
                    this.$emit('input',this.curPage);
                }
            },
            firstPage(){
                this.curPage=1;
                this.$emit('input',this.curPage);
            },
            lastPage(){
                this.curPage=this.pageCount;
                this.$emit('input',this.curPage);
            },
            doFocus(){
                this.dispPage = this.curPage;
            },
            doBlur(){
                this.dispPage = '';
            },
            dispPageChange(){
                this.curPage = parseInt(this.dispPage);
                this.$emit('input',this.curPage);
            },
        },
        watch: {
            value: function (newVal, oldVal) {
              this.curPage = newVal;
            }
        }
    }
</script>

<style>
    .page_nav_block{
        flex: 0;
        display: flex;
        padding: 0.5rem;
    }

    .page_nav{
        width: 1rem;
        /*display: inline-block;*/
        text-align: center;
        height: 100%;
        cursor: pointer;
        line-height: 1.5rem;
    }

    .page_nav_input{
        border: none;
        text-align: center;
        width: 8rem;
        background: transparent;
    }
</style>
