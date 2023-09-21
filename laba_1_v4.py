import re
import logging

logging.basicConfig(level=logging.DEBUG)


class Analyzer:
    def __init__(self, expression):
        self.expression = expression.replace(' ', '')
        self.end_index = 0
        self.end_of_expression = len(expression)
        self.items = []
        self.token_value = None
        self.have_error = False
        self.type_last = 'START'
        self.token_types = {
            'FLOAT': {
                'regex': '^\d+\.\d+',
                'can_be_with': ['FUNC', 'ALG', 'PAR_L', 'START'],
                'can_be_at_end': True,
            },
            'NUM': {
                'regex': '^\d+',
                'can_be_with': ['FUNC', 'ALG', 'PAR_L', 'START'],
                'can_be_at_end': True,
            },
            'FUNC': {
                'regex': '(^[a-zA-Z]+)\(',
                'can_be_with': ['ALG', 'PAR_L', 'START'],
                'can_be_at_end': False,
            },
            'VAR': {
                'regex': '^[a-zA-Z]+',
                'can_be_with': ['FUNC', 'ALG', 'PAR_L', 'PAR_R', 'START'],
                'can_be_at_end': True,
            },
            'ALG': {
                'regex': '^[+\-*/]',
                'can_be_with': ['NUM', 'FLOAT', 'VAR', 'PAR_R'],
                'can_be_at_end': False,
            },
            'PAR_L': {
                'regex': '^\(',
                'can_be_with': ['VAR', 'ALG', 'PAR_L', 'START'],
                'can_be_at_end': False,
            },
            'PAR_R': {
                'regex': '^\)',
                'can_be_with': ['NUM', 'FLOAT', 'VAR', 'PAR_R'],
                'can_be_at_end': True,
            },
            # 'COMA':{
            #     'regex': '^,',
            #     'can_be_with': ['NUM', 'FLOAT', 'VAR'],#'PAR_L' ,'PAR_R' can be if in function   # noqa: E501
            #     'can_be_at_end': False,
            # },
            'END': {
                'regex': '^$',
                'can_be_with': ['NUM', 'FLOAT', 'VAR', 'PAR_R'],
                'can_be_at_end': True,  # must be
            },
        }

    def error(self, message):
        self.have_error = True
        start = self.end_of_expression - (self.end_of_expression-self.end_index)-1
        err = f'{message}. At position: {self.end_index}. \t{self.expression[:start]} "{self.token_value}" {self.expression[self.end_index:]}'  # noqa: E501
        logging.error(err)

    def get_next_token(self):
        for type_token in self.token_types:
            token = re.search(self.token_types[type_token]['regex'], self.expression[self.end_index:])  # noqa: E501
            if token:
                self.end_index += token.span()[1]
                self.token_value = token.group()
                return type_token, token
        else:
            self.token_value = self.expression[self.end_index]
            self.end_index += 1
            self.error('Cant identify element')
            return self.type_last, None

    def parse(self):
        opened_parenthesis = 0
        stop = False

        while (not stop):
            type_token, token = self.get_next_token()
            if token:

                if self.type_last not in self.token_types[type_token]['can_be_with']:
                    self.error(
                        f'"{self.type_last}" cant be with "{type_token}"')

                if type_token == 'FUNC':
                    opened_parenthesis += 1
                    func_name = self.token_value.replace('(', '')
                    self.items.append((type_token, func_name))
                    self.token_value = '('

                elif type_token == 'PAR_L':
                    opened_parenthesis += 1

                elif type_token == 'PAR_R':
                    opened_parenthesis -= 1
                    if opened_parenthesis < 0:
                        self.error(
                            'Closed parenthesis ")" cant exist without "("')

                elif type_token == 'END':
                    if self.token_types[type_token]['can_be_at_end'] == False:  # noqa: E712, E501
                        self.error(f'Expression cant end with "{type_token}"')
                    if self.end_index == 0:
                        self.error('Empty string')
                    if opened_parenthesis > 0:
                        self.error(f'Parenthesis is not closed {opened_parenthesis} times')  # noqa: E501
                    stop = True

                self.type_last = type_token
                self.items.append((type_token, self.token_value))

        if self.have_error:
            logging.error("Expression have error.")
            return None
        else:
            logging.info("Expression passed.")
            print(self.items)
            return self.items


while True:
    expr = input("Input:\n")
    a = Analyzer(expr).parse()
