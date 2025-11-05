# CPY

As a language I really want to like python. However the syntax of python makes it really difficult to like. To solve this problem CPY consists of a token-level transpiler to convert python into an intermediate C-like syntax for viewing and editing, then back to original python code while preserving whitespace, comments, and everything else. This means you can edit python code seamlessly without ever having to touch python syntax.

Features:

- `def` is now `func`
  - variables named `func` are now named `def`
- Comments use `/* ... */` instead of `# ...`
  - to escape comments use `{code} /* ... \*/ ... */ {code}`
- `elif` has been replaced by `else if`
- Boolean logic has been replaced with C-like operators
  - `and    ->  &&`
  - `or     ->  ||`
  - `is     ->  ===`
  - `not    ->  !`
  - `is not ->  !==`
- `True` `False` and `None` are now `true` `false` and `NULL`
