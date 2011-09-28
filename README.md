RedBarrel
=========

Web builder and execution environment for Services server applications.


redbarrel
    |
  pistil : web server that runs the system

    |
    | -- appbuilder : a tool capable of creation an application online 
    |       |
    |      ----------
    |      |        |
    |   iPython    Web
    |
    | -- modules: a list of Python and JS modules
    |      |
    |    vmodule: a sandboxed Python or JS Module
    | 
    | -- applications
            |
           app1 : a wsgi app that runs with the DSL under a /root
            |
          mapper: creates a mapper using Routes and an AST, given a root
            |
          -------
          |     |
         ast   hook : responsible for the execution for one web service
                      pre/post calls, sandboxed call


