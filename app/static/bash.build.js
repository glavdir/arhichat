webpackJsonp([3],{188:function(t,e,s){"use strict";function i(t){s(226)}Object.defineProperty(e,"__esModule",{value:!0});var n=s(198),a=s(228),o=s(5),c=i,r=o(n.a,a.a,!1,c,"data-v-4e2a64cf",null);e.default=r.exports},198:function(t,e,s){"use strict";var i=s(24),n=s(65),a=s.n(n),o=new a.a.HTML2BBCode({weaknewline:!0});e.a={data:function(){return{pagetext:"",postid:"",time:0,editorOpts:{toolbar:{buttons:["bold","italic","underline","strikethrough","removeFormat"],diffTop:this.$isMobile.any?-50:-10},paste:{forcePlainText:!1,cleanPastedHTML:!0,cleanAttrs:["class","style","dir","text-align"],unwrapTags:["font","p"],cleanTags:["label","meta"],CleanReplacements:[]}}}},methods:{openBash:function(t){var e=this;this.$socket.emit("open_bash",t,function(t){e.postid=t.postid,e.pagetext=t.pagetext,e.time=t.time})},openPrevBash:function(){this.openBash({postid:this.postid,direction:"prev"})},openNextBash:function(){this.openBash({postid:this.postid,direction:"next"})},openLastBash:function(){this.openBash({postid:0,direction:"last"})},saveBash:function(t){var e=this;console.log(o.feed(this.pagetext).toString()),this.$socket.emit("save_bash",{postid:this.postid,pagetext:o.feed(this.pagetext).s},function(t){t?(e.postid=t.postid,e.time=t.time,e.flash("Сохранено","success",{timeout:2e3})):e.flash("ВНИМАНИЕ! Пост не сохранен!","error",{timeout:1e4})})},newBash:function(){this.postid="",this.pagetext="",this.time=0},editBash:function(t){this.pagetext=t.event.target.innerHTML}},computed:{postTitle:function(){return 0==this.time?"* новый пост":this.momentum(1e3*this.time).utc().add(this.$store.state.timezoneoffset,"hours").format("DD MMM YYYY")}},components:{"medium-editor":i.a},created:function(){this.openLastBash()}}},226:function(t,e,s){var i=s(227);"string"==typeof i&&(i=[[t.i,i,""]]),i.locals&&(t.exports=i.locals);s(3)("b56b8a54",i,!0)},227:function(t,e,s){e=t.exports=s(2)(!1),e.push([t.i,"",""])},228:function(t,e,s){"use strict";var i=function(){var t=this,e=t.$createElement,s=t._self._c||e;return s("div",{staticClass:"arhibash_root"},[s("div",{staticClass:"arhibash_header header"},[s("button",{staticClass:"bttn icon-conteiner",on:{click:t.openPrevBash}},[s("icon",{attrs:{name:"angle-left"}})],1),t._v(" "),s("button",{staticClass:"bttn icon-conteiner",on:{click:t.openNextBash}},[s("icon",{attrs:{name:"angle-right"}})],1),t._v(" "),s("span",{staticClass:"flex_splitter"},[t._v(t._s(t.postTitle))]),t._v(" "),s("button",{staticClass:"bttn icon-conteiner",attrs:{title:"Новый пост"},on:{click:t.newBash}},[s("icon",{attrs:{name:"plus"}})],1),t._v(" "),s("button",{staticClass:"bttn icon-conteiner",attrs:{title:"Сохранить"},on:{click:t.saveBash}},[s("icon",{attrs:{name:"floppy-o"}})],1)]),t._v(" "),s("div",{staticClass:"arhibash_conteiner"},[s("medium-editor",{staticClass:"arhibash_post",attrs:{text:t.pagetext,"custom-tag":"div",options:t.editorOpts,"data-placeholder":" "},on:{edit:function(e){t.editBash(e)}}})],1)])},n=[],a={render:i,staticRenderFns:n};e.a=a}});
//# sourceMappingURL=bash.build.js.map?0160a2bf80fd2c4cfa14