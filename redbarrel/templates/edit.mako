## -*- coding: utf-8 -*-
<html>
 <head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <title>${title}</title>
  <link rel="stylesheet" href="/__media__/redbarrel.css" type='text/css' />

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

<form name="edit_def" method="post"
      id="edit-ws"
      action="${approot}/__editor__/edit/${name}">

  <div>Name: <input type="text" name="name" value="${name}"/></div>
  <div><textarea name="description">${values['description']}</textarea></div>
  <div>
     <label for="url">Relative URL</label> <br/>
     ${approot}<input type="text" name="url" value="${values['url']}" style="width: 80%"/>

    </div>

  <div>Allowed methods
      <input type="checkbox" name="method" value="GET" checked>GET</input>
      <input type="checkbox" name="method" value="POST">POST</input>
      <input type="checkbox" name="method" value="PUT">PUT</input>
      <input type="checkbox" name="method" value="DELETE">DELETE</input>
      <input type="checkbox" name="method" value="HEAD">HEAD</input>
  </div>
  <div>
    Response Content Type<br/>
      <input type="radio" name="content-type"
             value="application/json"
             id="json" checked="true"/>
      <label for="json">application/json</label></br>

      <input type="radio" name="content-type" value="text/plain" id="text" />
      <label for="text">text/plain</label></br>

      <input type="radio" name="content-type" value="text/html" id="html"/>
      <label for="html">text/html</label></br>

      <input type="radio" name="content-type" value="other"
         id="other"/>
    <label for="Other">Other</label>

      <input type="text" name="content-type-value" value="text/acme"/>
    </div>
  <div>
    <label for="use">Function to use</label>
    <select name="use" id="use">
      %for callable in app.module.dir():
       %if '%s.%s' % (name, callable) == values['use']:
        <option value="${name}.${callable}" selected>
       %endif
       %if '%s.%s' % (name, callable) != values['use']:
        <option value="${name}.${callable}">
       %endif
           ${callable}
        </option>
      %endfor
    </select>
  </div>
  <div><input type="submit"></input></div>
</form>

</div>
</div>
</div>
</div>
</div>

</body>
</html>
