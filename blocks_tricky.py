arr = [1,2,3]
thing  = 2
code = "this is code"
i = 4
quote = 3
what = lambda x: x
otherthing = lambda x: x
def foo(x: int): return x
def bar(a: str, b: str): return {a: b}
if arr[1:2] == thing:
    otherthing()

if code[i-1:i+2] == quote * 3:
    what()

def converter_init(
        self, *,
        accept: TypeSet = {str},
        zeroes: bool = False
) -> None:
    format_unit = 'Z' if accept=={str, NoneType} else 'u'
    if zeroes:
        format_unit += '#'
        self.length = True
        self.format_unit = format_unit
    else:
        self.accept = accept

if 'a' if 1 == 1 else 'b' == 'a':
    print("yes")

def outer(a: int = 1, b = [i for i in range(3) if i]):
    def inner(x: str = 'a' if a == 1 else 'b', y = {k: v for k, v in {'x':1}.items() if k == 'x'}):
        if x[0:1] == ('a' if b[0] == 0 else 'b') and (a if b else 0):
            thing = { "weird": (lambda z: z if z else {"nested": [w for w in range(3) if w % 2 == 0]}) }
            if thing["weird"](None)["nested"][0:1] == [0]:
                return lambda: print("inside nested lambda")
        else: return {"key": "value"}  # inline suite here

    if (lambda f: f())(inner())['key':] if isinstance(inner, type(lambda:0)) else None:
        print("impossible")
    else:
        pass

class A:
    def __init__(self, data: dict[str, int] = { 'a': 1 if True else 0 }):
        self.data = data
        if 'a' in data: self.data['b'] = data['a'] + 1
        elif (cond := len(data)) > 0:
            while cond := cond - 1:
                self.data[cond] = cond
        else: return

    def method(self): return [v for v in self.data.values() if v % 2 == 0]
