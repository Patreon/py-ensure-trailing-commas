import ast, asttokens


class MissingTrailingCommaFinder(ast.NodeVisitor):
    def __init__(self, atok):
        self.atok = atok
        self.should_be_commas = set()

    def get_insersion_indexes(self):
        return sorted(token.endpos for token in self.should_be_commas)

    def get_insersion_coordinates(self):
        return sorted(token.end for token in self.should_be_commas)

    def skip_newlines(self, token, follower):
        iter_token = follower(token)
        while iter_token.string == '\n' and iter_token != token:
            iter_token = follower(iter_token)

        return iter_token

    def until_token(self, token, until, follower):
        token = follower(token, include_extra=True)
        while token.string != until:
            token = follower(token, include_extra=True)

        return token

    def find_trailing_commas(self, start_token, end_token):
        tokens = list(self.atok.token_range(start_token, end_token, include_extra=True))
        first_token, *rest, last_token = tokens

        start_line, start_column = first_token.start
        end_line, end_column = last_token.end
        if not rest or start_line == end_line:
            return

        *rest, should_be_newline = rest
        if not rest or should_be_newline.string != '\n':
            return

        *rest, should_be_comma = rest
        should_be_comma = self.atok.prev_token(self.atok.next_token(should_be_comma))  # Cleans comments
        if should_be_comma.string == ',':
            return

        self.should_be_commas.add(should_be_comma)

    def visit(self, node):
        if not hasattr(node, 'first_token') or not hasattr(node, 'last_token'):
            return

        super().visit(node)

    def visit_Call(self, node):
        super().generic_visit(node)

        if not node.args and not node.keywords:
            return

        # Generator expressions should not allow trailing comma. A bug in 3.6 allowed it but was fixed in 3.7
        # This is a special case when the generator is the only argument to the function call and is not surrounded
        # by parenthesis.
        if len(node.args) == 1 and isinstance(node.args[0], ast.GeneratorExp):
            return

        self.find_trailing_commas(node.first_token, node.last_token)

    def visit_Tuple(self, node):
        super().generic_visit(node)

        if not node.elts:
            return

        # Tuples are not always enclosed in parens. We should find the first non-newline token to find the parens
        last_token = self.skip_newlines(node.last_token, self.atok.next_token)
        if last_token.string != ')' and last_token.string != ']':
            last_token = node.last_token

        # Since we append commas at the end, we don't care about the above point for the starting token
        self.find_trailing_commas(node.first_token, last_token)

    def visit_List(self, node):
        super().generic_visit(node)

        if not node.elts:
            return

        self.find_trailing_commas(node.first_token, node.last_token)

    def visit_Set(self, node):
        super().generic_visit(node)

        if not node.elts:
            return

        self.find_trailing_commas(node.first_token, node.last_token)

    def visit_Dict(self, node):
        super().generic_visit(node)

        if not node.keys or not node.values:
            return

        self.find_trailing_commas(node.first_token, node.last_token)

    def visit_FunctionDef(self, node):
        super().generic_visit(node)

        arguments = node.args
        argument_list = arguments.args
        if arguments.vararg:
            argument_list.append(arguments.vararg)
        if arguments.kwonlyargs:
            argument_list.extend(arguments.kwonlyargs)
        if arguments.kwarg:
            argument_list.append(arguments.kwarg)
        if not argument_list:
            return

        self.find_trailing_commas(
            self.until_token(argument_list[0].first_token, '(', self.atok.prev_token),
            self.until_token(node.body[0].first_token, ')', self.atok.prev_token),
        )

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node):
        super().generic_visit(node)

        bases_list = node.bases
        if not node.bases:
            return

        self.find_trailing_commas(
            self.until_token(bases_list[0].first_token, '(', self.atok.prev_token),
            self.until_token(bases_list[-1].last_token, ')', self.atok.next_token),
        )


def find_missing_trailing_commas(source_code, *, filename='<unknown>'):
    atok = asttokens.ASTTokens(source_code, filename=filename, parse=True)
    comma_finder = MissingTrailingCommaFinder(atok)
    comma_finder.visit(atok.tree)

    return comma_finder


def get_insertion_indexes(source_code):
    return find_missing_trailing_commas(source_code).get_insersion_indexes()
