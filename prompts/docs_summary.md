# Here are your instructions:

**Your task is to create a documentation of the code you are given.**

## Here is what you should do:

Answer in a formal and informative style.
Since the task is to write a documentation, return *only* the documentation, no other personal insertion are allowed from.

Outline the general workflow in a sequence diagram using plantuml syntax.
If appropriate, use other UML diagrams to describe general information about the project, using plantuml syntax. For clarification make sure to lable each arrow, association, etc. you are making.
Always display plantuml syntax in a markdown codeblock:
{{TAG_UML_<name>}}
```plantuml
@startuml
% ...
@enduml
```

At the start summarize what the project does, then follow the following steps:

Repeat this for each package:
- Write a summary of the purpose of each package
- create a component diagram in plantuml syntax explaining the package
- a short list of other packages that access this package
- list a components of this single package

Each component description should include:
- name of component
- path to component
- description of the purpose of the component
- internal used parameters, the datatype, default value (if exists), a short description of their purposes in a table
- external used parameters, the datatype, default value (if exists), a short description of their purposes (if existing) in a table
- a uml-class-diagramm in plantuml syntax explaining the components structure
- if the content is suitable you may create additional diagrams in plantuml syntax

Each time you are writing plantuml code, place the tag `{{TAG_UML_<name>}}` before. Give the tag an unique name.
