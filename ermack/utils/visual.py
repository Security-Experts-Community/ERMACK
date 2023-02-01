logo = """
                                       ▄
                                      ██░
                                     ███░░
                                 ▄█▀▀███░░█▄
                              ▄█▀    ███░░  ▀█▄
                             █▀      ███░░     ▀█▄
                           ██        ███░░       ▀█
                          █▌         ███░░        ▐█
                         █▌          ███░░         ▀█
                        ▐█▄▄    ▄▄▄▄▓▓██▓█░▄▄▄▄    ▄▄█▌
                        █   ▀▀▀▀▀▀▀▀▓▓██▓█░██▀▀▀▀▀▀   █▄
                      ▄█             ███░░            ▀▌
                      █              ███░░             █
                      █     ██████▌ ▀███░░▀ ██████     █▌
                      █      ███████▄ ▀█▀ ▄██████      █
                     █▌    ▄██████████▄ ▄█████████▄    ▐█
                    ▐█    ███   ▀▀▀▀▀████▀▀▀▀▀▀  ▀██    ▓▌
                    █    ▀██▄ ▄▄ '   ███▌    ' ▄▄ ██▀    █▄
                   █      ████████▌▄▓███▌ ▄ ████████      █
                  █▌      ▐█████████▓███▌ █████████       ▐█
                 ▐█          ▀▀█████▓███▌  ████▀           █▌
                ▄█            ▐████▓█████▌  ███             █▄
                █             ██████▌ ▀▀  ██████             █
               █▓▄▌     █    ▀▀▀      ▄▄     ▀▀▀▀    █     ▀▄▐█
              ▐███     ██       ▄██▀▀▀  ▀▀▀██▄       ██     ███▌
              ▐▄█     ▐██     ██    ▓▓▓▓▓▓    ██▄    ██▌     █▌
               █       ▀███▄████              ████████▀       █▄
               ▀█        ▀██████████████████████████▀        █▀
                 █         ████████████████████████        ▄█
                  ▀█▄       ▀▀▀   ▀████████▀   ▀▀▀       ▄█▀
                    ▀█               ▀▀▀▀               █▀
                     ▀▀▌                              ▄█
                       ▀█▄▄▄█▀▀▀▀█▄        ▄█▀▀▀▀█▄▄▄█▀
                                   ▀▀█▄▄▄█▀

oooooooooooo ooooooooo.   ooo        ooooo   .oo.       .oooooo.   oooo    oooo
`888'     `8 `888   `Y88. `88.       .888' .88' `8.    d8P'  `Y8b  `888   .8P'
 888          888   .d88'  888b     d'888  88.  .8'   888           888  d8'
 888oooo8     888ooo88P'   8 Y88. .P  888  `88.8P     888           88888[
 888    "     888`88b.     8  `888'   888   d888[.8'  888           888`88b.
 888       o  888  `88b.   8    Y     888  88' `88.   `88b    ooo   888  `88b.
o888ooooood8 o888o  o888o o8o        o888o `bodP'`88.  `Y8bood8P'  o888o  o888o
-------------------------------------------------------------------------------
Enterprise Response Model & Common Knowledge"""


material_icons_style = """
.response_action_impl {
  color: #00b067;
  -webkit-transform:rotate(180deg);
  -moz-transform: rotate(180deg);
  -ms-transform: rotate(180deg);
  -o-transform: rotate(180deg);
  transform: rotate(180deg);
}
.response_action {
  color: #ccbc02;
}
.response_playbook {
  color: #00b067;
}
.threat {
  color: #d40641;
}
.software {
  color: #ccbc02;
}
.artifact {
  color: #00b067;
}
.external_link {
  color:  #807d7e;
}
.tag {
  color:  #ccbc02;
}
.requirements {
  color: #00b067;
}
.severity_high {
  color: #d40641;
}
.severity_medium {
  color: #d18d04;
}
.severity_other {
  color:  #807d7e;
}
.status_testing {
  color: #d18d04;
}
.status_buggy {
  color: #d40641;
}
.status_approved {
  color: #00b067;
}
.status_other {
  color:  #807d7e;
}
    """

material_search_html = """
{% extends "base.html" %}
{% block config %}
{{ super() }}
{% if "localsearch" in config["plugins"] %}
<script src="{{ 'assets/javascripts/iframe-worker.js' | url }}"></script>
<script src="{{ 'search/search_index.js' | url }}"></script>
{% endif %}
{% endblock %}
"""

material_search_js = """
"use strict";(()=>{function d(t,e){parent.postMessage(t,e||"*")}function c(...t){return t.reduce((e,n)=>e.then(()=>new Promise(r=>{let o=document.createElement("script");o.src=n,o.addEventListener("load",()=>r()),document.body.appendChild(o)})),Promise.resolve())}function m(){let t=document.createElement("iframe");return t.width=t.height=t.frameBorder="0",t}var s=class{constructor(e,n){this.url=e;this.onerror=null;this.onmessage=null;this.onmessageerror=null;this.handleMessage=e=>{e.source===this.worker&&(e.stopImmediatePropagation(),this.dispatchEvent(new MessageEvent("message",{data:e.data})),this.onmessage&&this.onmessage(e))};this.handleError=(e,n,r,o,i)=>{if(n===this.url.toString()){let a=new ErrorEvent("error",{message:e,filename:n,lineno:r,colno:o,error:i});this.dispatchEvent(a),this.onerror&&this.onerror(a)}};if(typeof n!="undefined")throw new TypeError("Options are not supported for iframe workers");let r=new EventTarget;this.addEventListener=r.addEventListener.bind(r),this.removeEventListener=r.removeEventListener.bind(r),this.dispatchEvent=r.dispatchEvent.bind(r),document.body.appendChild(this.iframe=m()),this.worker.document.open(),this.worker.document.write(`<html><body><script>postMessage=${d};importScripts=${c};addEventListener("error",ev=>{parent.dispatchEvent(new ErrorEvent("error",{filename:"${e}",error:ev.error}))})<\/script><script src="${e}?${+Date.now()}"><\/script></body></html>`),this.worker.document.close(),window.addEventListener("message",this.handleMessage),window.onerror=this.handleError,this.ready=new Promise((o,i)=>{this.worker.onload=o,this.worker.onerror=i})}terminate(){document.body.removeChild(this.iframe),window.removeEventListener("message",this.handleMessage),window.onerror=null}postMessage(e){this.ready.catch().then(()=>{this.worker.dispatchEvent(new MessageEvent("message",{data:e}))})}get worker(){return this.iframe.contentWindow}};window.IFrameWorker=s;location.protocol==="file:"&&(window.Worker=s);})();
"""
