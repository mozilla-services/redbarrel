## -*- coding: utf-8 -*-
<html>
 <head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <title>RedBarrel</title>
  <link rel="stylesheet" href="/__media__/redbarrel.css" type='text/css' />
  <script src="/__media__/jquery.js"></script>

 </head>
 <body>

  <div class="header">
  <a href="/__main__"><img src="/__media__/home.png"/></a>
  <h1>${lib.name}.py</h1>


 </div>
 <div style="clear:both"></div>
  <div class="sphinxsidebar">
    <div class="sphinxsidebarwrapper">
     <h3>Callables</h3>
      <ul>
        <li>
         <ul>
          %for callable in lib.dir():
            <li>${callable}</li>
          %endfor
         </ul>
        </li>
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

 <form action="/__lib__/${lib.name}" method="POST" id="formsave">
  <input type="hidden" name="data" id="data" value="EMPTY"/>
 </form>

 <div id="editor">${lib.code}</div>

    <script src="/__media__/ace.js" type="text/javascript" charset="utf-8"></script>
    <script src="/__media__/theme-twilight.js" type="text/javascript" charset="utf-8"></script>
    <script src="/__media__/mode-python.js" type="text/javascript" charset="utf-8"></script>

    <script>
    window.onload = function() {
        window.editor = ace.edit("editor");
        window.editor.setTheme("ace/theme/twilight");
        var PyMode = require("ace/mode/python").Mode;
        window.editor.getSession().setMode(new PyMode());
    };
    </script>

</div>

</div>
</div>
</div>
</div>
</body>
</html>
