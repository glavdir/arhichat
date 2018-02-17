<template>
    <div>
        <div class="panelHeader" @ckick="openMenu">
            <dropdown :class-name="'panelSelect'" :closeOnClick="true">
                <template slot="btn">
                    <div class="panelTitle">{{curPanel.title}}</div>
                </template>
                <template slot="body">
                    <template v-for="(pnl,key) in panels">
                        <div class="panelLabel" v-if="!pnl.isSelect" @click="swichPanel(pnl,key)">
                            <ul>{{ pnl.title }}</ul>
                        </div>
                    </template>
                    <!--<label>Скрыть вторую панель</label>-->
                </template>
            </dropdown>
            <div class="panelFlex"> </div>
            <slot name="kong"></slot>
            <div v-if="isAltPanel" class="panelOpenClose icon-cancel" @click = "closePanel">
            </div>
            <div v-if="!isAltPanel" class="panelOpenClose icon-right-open" @click = "openPanel">
            </div>
        </div>
        <div class="panelContent">
            <component v-bind:is="curPanel.component"/>
        </div>
    </div>
</template>

<script>
	import Dropdown from 'bp-vuejs-dropdown';
    import global from '../global.js';

    export default {
	    props:['panel', 'panels', 'panelName', 'isAltPanel', 'altPanelName'],
		name: "panel",
        components:{'dropdown':Dropdown},
        computed:{
	        curPanel:function () {
                return this.panels[this.$store.state.panels[this.panelName]]
            }
        },
        methods:{
	        openMenu(){
	            // this.$refs.dropdown.isHidden = false;
                // console.log(this.$refs.dropdown);
            },
            updateURL(){
                var queryPar = {};
                if (this.$store.state.panels.left!=undefined){
                    queryPar['left'] = this.$store.state.panels.left;
                }
                if (this.$store.state.panels.right!=undefined){
                    queryPar['right'] = this.$store.state.panels.right;
                }
	            this.$router.push({path: '/', query: queryPar});
            },
	        swichPanel(pnl,key){
                this.$store.commit('setPanel',{panel:this.panelName,  param:key});
                this.updateURL();
            },
            closePanel(){
	            this.$store.commit('closePanel',{panel:this.panelName});
	            this.updateURL();
	            // this.$bus.$emit('panelResize');
                this.$nextTick(function () {
                    global.set_chat_users_width();
                });            },
            openPanel(){
	            this.$store.commit('openPanel',{panel:this.altPanelName});
	            this.updateURL();
	            // this.$bus.$emit('panelResize');
                this.$nextTick(function () {
                    global.set_chat_users_width();
                });            },
        },
        mounted(){
            this.openThread = (data) => {
                if (this.panelName==data.panel) {
                    this.updateURL();
                }
            };
            this.$bus.$on("openThread", this.openThread);
        },
        beforeDestroy: function() {
            this.$bus.$off("openThread", this.openThread);
        },
    }
</script>

<style>
    .panelHeader{
        height: 2rem;
        width: 100%;
        background: #444;
        display: flex;
    }

    .panelTitle{
        line-height: 2rem;
        color: white;
        flex: 1;
        /*margin-left: 0.25rem;*/
        /*margin-right: 0.25rem;*/
    }

    .panelFlex{
        line-height: 2rem;
        color: white;
        flex: 1;
    }

    .panelContent{
        height: calc(100% - 2rem);
        /*margin: 0.5rem;*/
        /*box-sizing: border-box;*/
        /*border: 1px solid lightgrey;*/
        /*border-radius: 0.2rem;*/
    }

    .panelSelect-bp__btn{
        height: 2rem;
        box-sizing: border-box;
        border: none !important;
        color: white;
        padding: 0.5rem !important;
    }

    .panelSelect-bp__btn--active{
        background: transparent !important;
    }

    .panelOpenClose{
        height: 2rem;
        line-height: 2rem;
        margin-left: 0.5rem;
        margin-right: 0.5rem;
        cursor: pointer;
        color: white;
    }

    .panelLabel{
        margin: 0.25rem;
        cursor: pointer;
    }

    .panelOpenClose:hover{
        color: lightgrey;
    }

</style>
