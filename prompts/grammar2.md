Based on the {{language}} code input, create a formal grammar schema for it.

Follow the EBNF syntax for it:
- ignore comments in code
- use `program` as start variable
- when defining a variable, use `:` instead of `=`, e.g. like this: `variable: values`
- define each rule only once
- use lowercase variables, unless its a token then use uppercase
- use regular expressions to describe a token, put the regex in between `/regex/`, avoid using `/.*/`
- do not use variables or TOKENS in regular expressions
- do not forget to account for whitespaces
- do not return it as markdown
- do not end the line with an `;`
- at the end of the grammar add %import common.WS and %ignore WS
