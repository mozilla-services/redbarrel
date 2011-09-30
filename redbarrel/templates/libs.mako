## -*- coding: utf-8 -*-
<html>
 <head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <title>RedBarrel</title>
  <link rel="stylesheet" href="/__media__/redbarrel.css" type='text/css' />
 </head>
 <body>

 <div class="header">
 <img src="/__media__/barrel-small.jpg"></img>
 <h1>My Libs</h1>
 </div>
 <div style="clear:both"></div>
  <div class="sphinxsidebar">
    <div class="sphinxsidebarwrapper">
   <h3>Libs</h3>
  <ul>

<li>
<ul>
%for root, app in appviews:
%if root:
<li><a class="reference internal" href="${root}/__editor__">${root}</a></li>
%else:
<li><a class="reference internal" href="/__editor__">/</a></li>
%endif

%endfor
</ul>
</li>

</ul>

 </div>
      </div>

<div class="document">
      <div class="documentwrapper">
        <div class="bodywrapper">
          <div class="body">

<ul>
%for root, app in appviews:
%if root:
<li><a class="reference internal" href="${root}/__editor__">${root}</a></li>
%else:
<li><a class="reference internal" href="/__editor__">/</a></li>
%endif


%endfor
</ul>

<h2>Add a new Open Web Application</h2>
<form name="add_app" method="post"
      action="/__main__/add">
  <div>
  Name: <input type="text" value="changeme" name="name"></input>
  </div>
  <div>
  Description: <textarea name="description">Describe what this app does.</textarea>
  </div>
  <div>
  <input type="submit"></input>
  </div>
</form>


  <hr/>

</div>
</div>
</div>
</div>
</body>
</html>
