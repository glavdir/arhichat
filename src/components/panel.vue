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
                    <div class="panelLabelLine"></div>
                    <a class="panelLabel" href="http://arhimag.org">Форум</a>
                    <a class="panelLabel" href="http://wiki.arhimag.org">Архивики</a>
                </template>
            </dropdown>
            <div class="panelFlex"> </div>
            <slot name="kong"></slot>
            <div v-if="isAltPanel" class="panelOpenClose icon-conteiner" @click = "closePanel">
                <icon name = "close"></icon>
            </div>
            <div v-if="!isAltPanel" class="panelOpenClose icon-conteiner icon-right-open" @click = "openPanel">
                <icon name = "chevron-right"></icon>
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
            },
            openPanel(){
	            this.$store.commit('openPanel',{panel:this.altPanelName});
	            this.updateURL();
            },
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
        user-select: none;
    }

    .panelFlex{
        line-height: 2rem;
        color: white;
        flex: 1;
    }

    .panelContent{
        height: calc(100% - 2rem);
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
        display: block;
        text-decoration: none;
    }

    .panelLabelLine{
        margin: 0.25rem;
        height: 1px;
        border-bottom: 1px solid lightgrey;
        margin-top: 0.4rem;
        margin-bottom: 0.4rem;
    }

    .panelOpenClose:hover{
        color: lightgrey;
    }

</style>
