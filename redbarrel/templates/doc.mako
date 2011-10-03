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
 <h1>${title}</h1>  

 </div>
 <div style="clear:both"></div>

  <div class="sphinxsidebar">
    <div class="sphinxsidebarwrapper">
   <h3>Web Services</h3>
  <ul>
<ul>
%for name, def_ in defs.items():
<li><a class="reference internal" href="#${name}">${name}</a></li>
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
<h3><a href="${approot}/__editor__/editapp">Edit the code</a></h3>
  %if 'description' in options:
  ${rst2HTML(options['description'])}
  %endif

  %for name, def_ in defs.items():
  <div class='section service' id="${name}">
     <a class="action" href="${approot}/__editor__/edit/${name}">
        <img src="/__media__/edit.png"/>
     </a>
     <a class="action" href="${approot}/__editor__/delete/${name}">
        <img src="/__media__/delete.png"/>
     </a>

    <div class="title">
     %if 'method' in def_:
      ${'|'.join([str(v) for v in def_['method']])} ${def_['url']}
     %endif
     %if 'method' not in def_:
      ${name}
     %endif
    </div>
    %if 'description' in def_:
    <div class="description">
     ${rst2HTML(def_['description'])}
    </div>
    %endif

    %if 'use' in def_:
    <div class="description">
     The response is built by <a href="${which_lib(def_['use'])}">${def_['use']}</a>
    </div>
    %endif


     %if ('request-body' in def_ or 'request-headers' in def_):
     <h3>Request</h3>

     %if 'request-body' in def_:
      <h4>Body</h4>
      <p>${def_.describe('request-body')}</p>

      %if def_.has_rules('request-body'):
       <ul>
         %for trans in def_.translate('request-body', 'body'):
         <li>${trans}</li>
         %endfor
         </ul>
       %endif
      %endif

     %if 'request-headers' in def_:
      <h4>Headers</h4>

      <p>${def_.describe('request-headers')}</p>

      %if def_.has_rules('request-headers'):
       <ul>
         %for trans in def_.translate('request-headers', 'headers'):
         <li>${trans}</li>
         %endfor
         </ul>
       %endif
      %endif

     %endif


     %if ('response-body' in def_ or 'response-headers' in def_ or 'response-status' in def_):
     <h3>Response</h3>

     %if 'response-body' in def_:
      <h4>Body</h4>
      <p>${def_.describe('response-body')}</p>

      %if def_.has_rules('response-body'):
       <ul>
         %for trans in def_.translate('response-body', 'body'):
         <li>${trans}</li>
         %endfor
         </ul>
       %endif
      %endif

     %if 'response-status' in def_:
      <h4>Status</h4>
      <p>${def_.describe('response-status')}</p>

      %if def_.has_rules('response-status'):
       <ul>
         %for trans in def_.translate('response-status', 'status'):
         <li>${trans}</li>
         %endfor
         </ul>
       %endif
      %endif

     %if 'response-headers' in def_:
      <h4>Headers</h4>
      <p>${def_.describe('response-headers')}</p>

      %if def_.has_rules('response-headers'):
       <ul>
         %for trans in def_.translate('response-headers', 'headers'):
         <li>${trans}</li>
         %endfor
         </ul>
       %endif
      %endif
     %endif
  </div>
  %endfor

<hr/>

<script>
jQuery.fn.center = function () {
    this.css("position","absolute");
    this.css("top", (($(window).height() - this.outerHeight()) / 2) + $(window).scrollTop() + "px");
    this.css("left", (($(window).width() - this.outerWidth()) / 2) + $(window).scrollLeft() + "px");
    return this;
}


$(function() {
  $('a#ws-adder').click(function() {
    $('form#add-ws').show()
        .center();
  });
});

</script>

<form name="add_def" method="post"
      class="rounded"
      id="add-ws"
      action="${approot}/__editor__/newpath">
 <span class="close"
    onclick="$('form#add-ws').hide()">Close</span>

<h3>Add a web service</h3>

  <div>Name: <input type="text" name="name" value="somename"/></div>
  <div><textarea name="description">Describe what it does.</textarea></div>
  <div>
     <label for="url">Relative URL</label> <br/>
     ${approot}<input type="text" name="url" value="/somepath" style="width: 80%"/>

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
        <option value="app.${callable}">
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

</body>
</html>
