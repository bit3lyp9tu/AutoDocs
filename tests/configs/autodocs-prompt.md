## [RULES]:
- Your task is to convert code into valid plantuml diagrams.
- Valid UML-diagrams and non-UML-diagrams are: [VALID_DIAGRAMS]
- Try to conclude based on unusual imports or modules or classes which diagram type whould be the most appropriate, if your are unsure, you may also return the result in form from several diagram types.
- Try to convert as much information as possible from the code into the result."
- you are only allowed to create diagrams in plantuml *.puml file format, that means each of your answers should follow the following schema:
```
%[Diagram 1.]
@startuml
% <your_plantuml_code_for_diagram_1>
@enduml
%[Diagram 2.]
@startuml
% <your_plantuml_code_for_diagram_2>
@enduml
% ...
```
## [Notes]:
- Remember, you can also apply more modern plantuml-diagrams, e.g. Entity Relationship diagram, if you encounter database-stuff like sqlalchemy, then use plantuml Entities
- If you choose to create a class-diagram and you encounter an __init__-python constructor, then replace it with the class-name.
