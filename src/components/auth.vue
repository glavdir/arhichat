<template>
    <div class="login_form">
        <div class="login_group">
            <input v-model="username" type="text" placeholder="Имя" @keydown.enter="doAuth">
            <input v-model="userpass" type="password" placeholder="Пароль" @keydown.enter="doAuth">
            <button @click="doAuth">Вход</button>
        </div>
    </div>
</template>

<script>
    import Vue from 'vue';
    import axios from 'axios';
    import VueCookie from 'vue-cookie';
    import global from '../global.js';
    Vue.use(VueCookie);

	export default {
		name: "auth",
        data:function(){
            return {
                username:'',
                userpass:'',
            }
        },
        methods:{
		    doAuth(){
                if (this.username!='' && this.userpass!=''){
                    let this_app = this;
                    let params = {username:this.username, userpass:this.userpass};
                    axios.post(global.curdomain+'/api/do_auth/','auth',{withCredentials:true, params:params })
                        .then(function (response) {
                            // this_app.$cookie.set('bbsessionhash', response.data.sessionhash,   {expires: '1Y');
                            this_app.$cookie.set('bbpassword',    response.data.passwordhash,  {expires: '1Y'});
                            this_app.$cookie.set('bbuserid',      response.data.userid,  { expires: '1Y' });
                            location.reload();
                        });
                }
		    }
        }
	}
</script>

<style scoped>

</style>
