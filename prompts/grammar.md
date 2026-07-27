Based on the language input, create a formal grammar schema for it.

Follow the following syntax for it:
- ignore comments in code
- use lowercase variables, unless its a token then use uppercase
- use `program` as start variable
- define each rule only once
- use regular expressions to describe a token, put the regex in between `/regex/`, avoid using `/.*/`
- do not forget to account for whitespaces
- for `or` combiner, use `|`
- use a `?` suffix to a variable then its optional
- use a `+` suffix when one-or-many
- use a `*` suffix when zero-or-many
- use only one suffix per variable
- use this syntax for describing an expression: `variable: values`
- do not return it as markdown
