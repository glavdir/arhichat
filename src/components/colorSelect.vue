<template>
<click-outside :handler="handleClickOutside">
    <div class="rootColor" @click="startSelect">
        <div v-if="isSelect" class="colorlist">
            <div class="colorRow" v-for="colorline in colorlist">
                <div v-for="color in colorline" :key="color" :style="'background:'+color" class="bttn-color" @click="doSelect(color)"></div>
            </div>
        </div>
        <div class="colorMark">A</div>
        <div class="colorLine" :style="'background:'+value"></div>
    </div>
</click-outside>
</template>

<script>
    import ClickOutside from 'onclick-outside';

    export default {
        props:['value','colorlist'],
        data: function() {return {
            isSelect: false,
            // curColor:this.value
        }},
        methods: {
            doSelect: function (scolor) {
                // this.curColor = scolor;
                this.$emit('input', scolor);
            },
            startSelect: function () {
                this.isSelect=!this.isSelect;
            },
            handleClickOutside(e) {
                if (this.isSelect){
                    this.isSelect = false;
                }
            }
        },
        components:{
            ClickOutside
        },
        created(){
            // this.curColor=this.value;
            // console.log('!!!');
        }
    }
</script>

<style>

.bttn-color{
    width: 1.5rem;
    height: 1.5rem;
    /* border: 2px solid rgba(0,0,0,0.35); */
    box-sizing: border-box;
}

.colorlist{
    position: absolute;
    bottom: calc(100% + 1px);
    left: -200%;
    border: 1px solid lightgray;
    padding: 2px;
    background: white;
    display: table;
}

.rootColor{
    position: relative;
    line-height: 2rem;
    font-weight: bold;
}

.colorLine{
    width: 1.5rem;
    height: 0.3rem;
    margin: auto;
}

.colorRow{
    background: transparent;
    display: flex;
}

.colorMark{
    background: transparent;
    margin: 0 auto;
    text-align: center;
    margin-top: 0.1rem;
    height: 1.7rem;
}

</style>
