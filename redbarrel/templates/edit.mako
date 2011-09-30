## -*- coding: utf-8 -*-
<html>
 <head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <title>${title}</title>
  <link rel="stylesheet" href="/__media__/redbarrel.css" type='text/css' />
  <script src="/__media__/jquery.js"></script>

 </head>
 <body>
 <div class="header">
 <img src="/__media__/app.png"/>
 <a href="${approot}/__api__"><img src="/__media__/rbr.png"/></a>
 <a href="/__main__"><img src="/__media__/home.png"/></a>
 <h1>${title} - ${name}</h1>
 </div>
 <div style="clear:both"></div>

  <div class="sphinxsidebar">
    <div class="sphinxsidebarwrapper">
   <h3>Web Services</h3>
  <ul>
<ul>
%for name_, def_ in defs.items():
<li><a class="reference internal" href="#${name_}">${name_}</a></li>
%endfor
<li><a href="#" id="ws-adder">
&lt;add one&gt; </a></li>

</ul>

</ul>

 </div>
    <div class="sphinxsidebarwrapper">
   <h3>Mozilla Services</h3>
<ul>
<ul>
    <li><a class="#">Storage</a></li>
    <li><a class="#">E-Mail</a></li>
    <li><a class="#">Queuing</a></li>
    <li><a class="#">Notifications</a></li>
    <li><a class="#">Authentication</a></li>

</ul>
</ul>

<div style="clear:both"></div>
 </div>


      </div>


<div class="document">
      <div class="documentwrapper">
        <div class="bodywrapper">
          <div class="body">

<div id="editorContainer">
 <script>
   function save() {
     value = window.editor.getSession();
     window.document.getElementById("data").value = value;
     window.document.getElementById("formsave").submit();
   };

 </script>
 <img class="save" href="#" onclick="save();" src="/__media__/save.png"/>

 <form action="." method="POST" id="formsave">
  <input type="hidden" name="data" id="data" value="EMPTY"/>
 </form>

 <div id="editor">${path}</div>

    <script src="/__media__/ace.js" type="text/javascript" charset="utf-8"></script>
    <script src="/__media__/theme-twilight.js" type="text/javascript" charset="utf-8"></script>

    <script>
    window.onload = function() {
        window.editor = ace.edit("editor");
        window.editor.setTheme("ace/theme/twilight");
    };
    </script>

</div>
</div>
</div>
</div>
</div>

</body>
</html>
