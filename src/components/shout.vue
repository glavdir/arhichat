<template>
    <div class="shout" v-bind="{'data-sid': sid}"><!--
        --><span class="me_stars" v-if="me!='0'">*</span><!--
        --><span class="time_user"><!--
        --><span v-if="me=='0'" class="time" v-html="'['+datetime(time)+'] '"></span><!--datetime
        --><span class="user"
                    v-bind="{'data-pmid':s_user}"
                    v-html="user"
                    @click="tabOnClick(s_user)"
            ></span><a v-if="me=='0'"><span class="dots">:</span></a></span>
            <span class="msg_text" v-bind="{'id':'span'+sid, 'style':'color:'+color}" v-html="msg"></span><!--
        --><span class="me_stars" v-if="me!='0'">*</span>
    </div>
</template>

<script>
    export default {
        props: ['sid', 'me', 'time', 's_user', 'user', 'msg', 'color'],
        data: function() {
            return {};
        },
        methods: {
            doSelect: function() {
                this.value = !this.value;
                return this.$emit('input', this.value);
            },
            datetime: function(ms){
                return  this.momentum(ms*1000).utc().add(this.$store.state.timezoneoffset,'hours').subtract(0, 'days').calendar();//datetime(date);
            },
            tabOnClick (userid){
                this.$emit('tabOnClick',userid);
            }

        }
    };
</script>
