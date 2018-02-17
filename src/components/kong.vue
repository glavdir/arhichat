<template>
    <div class="kong" @click="do_reconnect">
        <img  v-if="opts.use_kong && big_kong" class="kong_img" :src="'../static/img/kong_challenge.gif'"/>
        <span v-if="opts.show_kong" class="kong_counter">{{kong_counter}}</span>
    </div>
</template>

<script>
	export default {
		name: "kong",
        data() {return {
            kong_time:new Date(),
            kong_counter:0
        }},
        methods:{
            calc_kong:function (data) {
                // setTimeout(this.calc_kong,1000);
                this.kong_counter = new Date() - this.kong_time;
            },
            do_reconnect(){
                this.kong_time = new Date();
                this.$socket.io.disconnect();
                this.$socket.io.open();
                console.log('King Kong Alive!!!');
            },
            safe_reconnect(){
                var thetime = Math.abs(new Date()-this.kong_time);
                if (thetime>3500){//||socket.disconnected
                    this.do_reconnect();
                }
            }
        },
        sockets:{
            ping:function (data) {
                this.kong_time = new Date();
            },
        },
        computed:{
		    opts(){
                return this.$store.state.opts;
            },
            big_kong(){
                return this.kong_counter>=5000
            }
        },
        created(){
            setInterval(this.calc_kong,1000);
            var this_app = this;
            window.onblur =function(){
                this_app.safe_reconnect();
                this_app.calc_kong();
            };
            window.onfocus = function(){
                this_app.safe_reconnect();
                this_app.calc_kong();
            };
        }
	}
</script>

<style>
    .kong{
        /*position: absolute;*/
        right: 2.2rem;
        height: 2rem;
        line-height: 2rem;
        color: white;
        display: flex;
        float: right;
        cursor: pointer;
    }

    .kong_counter{
        display: inline-block;
    }

    .kong_img{
        display: inline-block;
    }
</style>
