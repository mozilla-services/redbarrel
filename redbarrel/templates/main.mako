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
 <h1>RedBarrel</h1>
 </div>
 <div style="clear:both"></div>
  <div class="sphinxsidebar">
    <div class="sphinxsidebarwrapper">
     <h3>My Apps</h3>
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
            <li><a href="#" id="app-adder2">
                &lt;add one&gt; </a></li>
         </ul>
        </li>
      </ul>
    </div>
    <div class="sphinxsidebarwrapper">
     <h3>My Modules</h3>
      <ul>
        <li>
         <ul>
          %for lib in libraries:
            <li><a class="reference internal" href="/__lib__/${lib.name}">${lib.name}.py</a></li>
          %endfor
            <li><a href="#" id="lib-adder">
                &lt;add one&gt; </a></li>
         </ul>
        </li>
      </ul>
    </div>
  </div>

<div class="document">
      <div class="documentwrapper">
        <div class="bodywrapper">
          <div class="body">

%for root, app in appviews:
%if root:
<div class="app">
<a class="reference internal" href="${root}/__editor__">
<img src="/__media__/app.png"/><br/>
${root}
</a>
</div>
%else:
<div class="app">
<a class="reference internal" href="/__editor__">
<img src="/__media__/app.png"/>
</a>
</div>
%endif


%endfor
<div class="new">
<a href="#" id="app-adder">Add a new app...<br/>
<img src="/__media__/add.png"/>
</a>
</div>

<div style="clear: both"/>

<script>
jQuery.fn.center = function () {
    this.css("position","absolute");
    this.css("top", (($(window).height() - this.outerHeight()) / 2) + $(window).scrollTop() + "px");
    this.css("left", (($(window).width() - this.outerWidth()) / 2) + $(window).scrollLeft() + "px");
    return this;
}

$(function() {
  $('a#app-adder2').click(function() {
    $('form#add-app').show()
        .center();
  });
});


$(function() {
  $('a#app-adder').click(function() {
    $('form#add-app').show()
        .center();
  });
});

$(function() {
  $('a#lib-adder').click(function() {
    $('form#add-lib').show()
        .center();
  });
});

</script>

<form class="rounded" name="add_app" method="post"
      action="/__main__/add" id="add-app">
 <span class="close"
    onclick="$('form#add-app').hide()">Close</span>
 
<h3>Add a new app</h3>
    <div>
    <label for="name">Name</label>
    <input type="text" value="changeme" id="name"
           name="name"></input>
  </div>
  <div>
    <label for="description">Description</label>
    <textarea name="description" id="description">Describe what this app does.</textarea>
  </div>
  <hr/>
  <input type="submit" value="add"/>
  
</form>


<form class="rounded" name="add_lib" method="post"
      id="add-lib"
      action="/__main__/addlib" enctype="multipart/form-data">
  <span class="close"
    onclick="$('form#add-lib').hide()">Close</span>
 
 <h3>Add a new module</h3>

  <div>
    <label for="name">Name</label>
    <input type="text" style="width: 90%" value="changeme" id="name"
           name="name"></input>.py
  </div>
  <div>
    <label for="name">File (leave empty for a new module)</label>
    <input type="file" name="file" id="file"/>
  </div>
  <hr/>
  <input type="submit"></input>
</form>

</div>
</div>
</div>
</div>
</body>
</html>
