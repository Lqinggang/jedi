from jedi._compatibility import Parameter


class _SignatureMixin(object):
    def to_string(self):
        def param_strings():
            is_positional = False
            is_kw_only = False
            for n in self.get_param_names():
                kind = n.get_kind()
                is_positional |= kind == Parameter.POSITIONAL_ONLY
                if is_positional and kind != Parameter.POSITIONAL_ONLY:
                    yield '/'
                    is_positional = False

                if kind == Parameter.VAR_POSITIONAL:
                    is_kw_only = True
                elif kind == Parameter.KEYWORD_ONLY and not is_kw_only:
                    yield '*'
                    is_kw_only = True

                yield n.to_string()

            if is_positional:
                yield '/'

        s = self.name.string_name + '(' + ', '.join(param_strings()) + ')'
        annotation = self.annotation_string
        if annotation:
            s += ' -> ' + annotation
        return s

    def get_param_names(self, resolve_stars=True):
        param_names = self._function_context.get_param_names()
        if self.is_bound:
            return param_names[1:]
        return param_names


class AbstractSignature(_SignatureMixin):
    def __init__(self, context, is_bound=False):
        self.context = context
        self.is_bound = is_bound

    @property
    def name(self):
        return self.context.name

    @property
    def annotation_string(self):
        return ''

    def bind(self, context):
        raise NotImplementedError


class TreeSignature(AbstractSignature):
    def __init__(self, context, function_context=None, is_bound=False):
        super(TreeSignature, self).__init__(context, is_bound)
        self._function_context = function_context or context

    def bind(self, context):
        return TreeSignature(context, self._function_context, is_bound=True)

    @property
    def _annotation(self):
        # Classes don't need annotations, even if __init__ has one. They always
        # return themselves.
        if self.context.is_class():
            return None
        return self._function_context.tree_node.annotation

    @property
    def annotation_string(self):
        a = self._annotation
        if a is None:
            return ''
        return a.get_code(include_prefix=False)

    def get_param_names(self, resolve_stars=True):
        params = super(TreeSignature, self).get_param_names()
        if resolve_stars:
            from jedi.evaluate.star_args import process_params
            params = process_params(params)
        return params


class BuiltinSignature(AbstractSignature):
    def __init__(self, context, return_string, is_bound=False):
        super(BuiltinSignature, self).__init__(context, is_bound)
        self._return_string = return_string

    @property
    def annotation_string(self):
        return self._return_string

    @property
    def _function_context(self):
        return self.context

    def bind(self, context):
        assert not self.is_bound
        return BuiltinSignature(context, self._return_string, is_bound=True)


class SignatureWrapper(_SignatureMixin):
    def __init__(self, wrapped_signature):
        self._wrapped_signature = wrapped_signature

    def __getattr__(self, name):
        return getattr(self._wrapped_signature, name)
