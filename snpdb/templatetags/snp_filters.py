from django import template

register = template.Library()


@register.filter
def integer_comparison(value, arg):
    if arg[0] == arg[1]:
        return True
    else:
        return False


@register.tag
def make_list(parser, token):
    bits = list(token.split_contents())
    if len(bits) >= 4 and bits[-2] == "as":
        varname = bits[-1]
        items = bits[1:-2]
        return MakeListNode(items, varname)
    else:
        raise template.TemplateSyntaxError("%r expected format is 'item [item ...] as varname'" % bits[0])


class MakeListNode(template.Node):
    def __init__(self, items, varname):
        self.items = map(template.Variable, items)
        self.varname = varname

    def render(self, context):
        context[self.varname] = [i.resolve(context) for i in self.items]
        return ""

@register.filter
def empty_effect(value):
    if value:
        return False
    else:
        return True

@register.filter
def no_effect(value):
    if value == 'None' or value is None:
        return False
    else:
        return True


@register.filter
def get_type(value):
    if type(value) is list:
        return True
    else:
        return False