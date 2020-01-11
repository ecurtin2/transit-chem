from inspect import isfunction, getmembers, getattr_static, getdoc
from typing import Dict, List, Any, Callable
from pathlib import Path


from inspect import signature
import attr

from quantized import (
    atom,
    basis,
    config,
    molecule,
    hopping_matrix,
    time_evolution,
    potentials,
    operators,
    elements,
    utils,
    validation,
)


def markdown_table(d: Dict[str, List[Any]], width: int = 10, none: str = "-") -> str:
    cstr = lambda x: str(x).center(width) if x is not None else none.center(width)

    header = "|" + "|".join(map(cstr, d)) + "|"
    br = "|" + "|".join("-" * width for _ in d) + "|"
    rows = ["|" + "|".join(map(cstr, row)) + "|" for row in zip(*d.values())]
    return "\n".join([header, br] + rows)


def formatted_signature(f: Callable, fname: str = None) -> str:
    if isfunction(f):
        sig = signature(f)
    elif isinstance(f, type):
        sig = signature(f.__init__)

    else:
        raise TypeError(f"Cant get sig for {f}")

    params = [str(v) for v in sig.parameters.values()]
    # get rid of self if class
    if isinstance(f, type):
        params = params[1:]
        ret = ")"
    else:
        ret = f") -> {sig.return_annotation}"
    param_s = ", ".join(params) + ret
    if len(param_s) > 60:
        param_s = "\n    " + ",\n    ".join(params) + "\n" + ret

    if fname is None:
        fname = f.__name__
    sig = f"{fname}({param_s}"

    return "```\n" + sig + "\n```\n"


def attrs_docs_from_module(m) -> str:
    attrs_classes = [
        v for k, v in m.__dict__.items() if attr.has(v) and k in m.__all__ and isinstance(v, type)
    ]
    docs = [getdoc(cls) for cls in attrs_classes]
    sigs = [formatted_signature(cls) for cls in attrs_classes]
    headers = [f"###{cls.__name__}\n\n" for cls in attrs_classes]
    member_docs = [get_member_docs(cls) for cls in attrs_classes]
    doc_sigs = [h + s + d + m for h, d, s, m in zip(headers, docs, sigs, member_docs)]
    return "\n\n --- \n\n".join(doc_sigs) + "\n\n"


def get_method_sigs(methods, cls) -> List[str]:
    sigs = []
    for x in sorted(methods, key=lambda x: x[0]):
        name = x[0]
        doc = getdoc(x[1])
        try:
            sig = formatted_signature(x[1], fname=f"{cls.__name__}.{name}")
        except TypeError:
            sig = ""
        escaped_name = name.replace("_", "\_")
        sigs.append(f"#####{escaped_name}\n{sig}\n\n{doc}")
    return sigs


def get_member_docs(cls) -> str:
    methods = getmembers(cls)
    staticmethods = []
    classmethods = []
    normal_methods = []
    properties = []
    dunder_methods = []
    for name, m in methods:
        # Skip single underscore methods
        if name.startswith("_") and not name.startswith("__"):
            continue
        if name.startswith("__") and not hasattr(m, "include_in_docs"):
            continue
        if hasattr(m, "include_in_docs") and not m.include_in_docs:
            continue

        meth = getattr_static(cls, name)
        if name.startswith("__"):
            dunder_methods.append((name, m))
        elif isinstance(meth, staticmethod):
            staticmethods.append((name, m))
        elif isinstance(meth, property):
            properties.append((name, m))
        elif isinstance(meth, classmethod):
            classmethods.append((name, m))
        else:
            normal_methods.append((name, m))

    if normal_methods:
        method_str = "\n\n####Methods\n\n" + "\n".join(get_method_sigs(normal_methods, cls))
    else:
        method_str = ""

    if properties:
        prop_str = "\n\n####Properties\n\n" + "\n".join(get_method_sigs(properties, cls))
    else:
        prop_str = ""

    if staticmethods:
        static_str = "\n\n####Static Methods\n\n" + "\n".join(get_method_sigs(staticmethods, cls))
    else:
        static_str = ""

    if dunder_methods:
        dunder_str = "\n\n####Dunder Methods\n\n" + "\n".join(get_method_sigs(dunder_methods, cls))
    else:
        dunder_str = ""

    return method_str + "\n\n" + prop_str + "\n\n" + static_str + "\n\n" + dunder_str


def func_docs_from_module(m) -> str:
    funcs = [v for k, v in m.__dict__.items() if isfunction(v) and k in m.__all__]
    sigs = [formatted_signature(f) for f in funcs]
    docstrings = [getdoc(f) for f in funcs]
    return "\n\n".join(f"###{f.__name__}\n\n{s}\n\n{d}" for f, d, s in zip(funcs, docstrings, sigs))


def autodoc_module(m) -> str:
    module_docstring = getdoc(m)
    if module_docstring is None:
        module_docstring = ""
    else:
        module_docstring += "\n\n"

    return (
        f"# {m.__name__} Module"
        + "\n\n"
        + module_docstring
        + "\n\n"
        + "## Classes"
        + "\n\n---\n\n"
        + attrs_docs_from_module(m)
        + "\n\n"
        + "## Functions"
        + "\n\n----\n\n"
        + func_docs_from_module(m)
    )


### Elements
attributes = ["name", "z", "voie", "alpha"]
d = {a: [getattr(e, a) for e in elements.all_elements] for a in attributes}
elements_table = "### Table of Elements\n\n" + markdown_table(d)

md = "\n\n --- \n\n".join([elements.Element.__doc__, elements_table])
Path("elements.md").write_text(md)


### Basis

Path("basis.md").write_text(autodoc_module(basis))

### Config
Path("config.md").write_text(autodoc_module(config))

### Molecule
Path("molecule.md").write_text(autodoc_module(molecule))

### Hopping_matrix
Path("hopping_matrix.md").write_text(autodoc_module(hopping_matrix))

### Time evolution
Path("time_evolution.md").write_text(autodoc_module(time_evolution))

### Potentials
Path("potentials.md").write_text(autodoc_module(potentials))

### Operators
Path("operators.md").write_text(autodoc_module(operators))

### Atom
Path("atom.md").write_text(autodoc_module(atom))

###  Utils
Path("utils.md").write_text(autodoc_module(utils))

###  Validation
Path("validation.md").write_text(autodoc_module(validation))
