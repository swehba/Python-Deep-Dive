from string import ascii_lowercase


class ParameterNameGenerator:
    def __init__(self):
        self.next_index = 0

    def __next__(self):
        if self.next_index == len(ascii_lowercase):
            raise StopIteration
        param_name = ascii_lowercase[self.next_index]
        self.next_index += 1
        return param_name

    def __iter__(self):
        return self

    def reset(self):
        self.next_index = 0


# noinspection PyMethodMayBeStatic
class FunctionSignatureCreator:

    def __init__(self):
        self.state = ''
        self.past_states = set()

        self.param_name_generator = ParameterNameGenerator()
        self.param_list = []

        self.positional_params = 0
        self.required_positional_params = 0
        self.optional_positional_params = 0
        self.variable_positional_params = False

        self.keyword_params = 0
        self.variable_keyword_params = False
        self.require_names_for_keyword_params = False
        self.keyword_param_is_required = []

    def were(self, n):
        return 'was' if n == 1 else 'were'

    def plural(self, s, n):
        return s if n == 1 else s + 's'

    def reset(self):
        self.past_states.clear()
        self.param_list.clear()
        self.param_name_generator.reset()

        self.positional_params = 0
        self.required_positional_params = 0
        self.optional_positional_params = 0
        self.variable_positional_params = False

        self.keyword_params = 0
        self.variable_keyword_params = False
        self.require_names_for_keyword_params = False
        self.keyword_param_is_required.clear()

    @property
    def next_state(self):
        return self.state

    @next_state.setter
    def next_state(self, s):
        # If the next state is a past state, print a blank line and remove it.
        if s in self.past_states:
            print()
            self.past_states.remove(s)

        self.past_states.add(self.state)
        self.state = s

    def run(self):
        self.next_state = 'A'
        while self.state != 'DONE':
            if self.state == 'A':
                self.reset()
                answer = input(f'{self.state}: How many NAMED POSITIONAL PARAMETERS (0, 1, ...)? ').upper()
                if answer in self.past_states:
                    self.next_state = answer
                else:
                    self.positional_params = int(answer)
                    if self.positional_params == 0:
                        self.next_state = 'C'
                    else:
                        self.next_state = 'B'

            elif self.state == 'B':
                answer = input(f'{self.state}: How many of those are REQUIRED '
                               f'(0 to {self.positional_params})? ').upper()
                if answer in self.past_states:
                    self.next_state = answer
                else:
                    self.required_positional_params = int(answer)
                    if self.required_positional_params > self.positional_params:
                        print(f"Oops, that's too many. You said there {self.were(self.positional_params)} only "
                              f"{self.positional_params} "
                              f"{self.plural('positional parameter', self.positional_params)}. Let's start over...")
                        self.next_state = 'A'
                    else:
                        self.optional_positional_params = self.positional_params - self.required_positional_params
                        self.next_state = 'C'

            elif self.state == 'C':
                answer = input(f'{self.state}: Any VARIABLE POSITIONAL PARAMETERS (y/n)? ').upper()
                if answer in self.past_states:
                    self.next_state = answer
                else:
                    self.variable_positional_params = (answer == 'Y')
                    self.next_state = 'D'

            elif self.state == 'D':
                answer = input(f'{self.state}: How many NAMED KEYWORD PARAMETERS (0, 1, ...)? ').upper()
                if answer in self.past_states:
                    self.next_state = answer
                else:
                    self.keyword_params = int(answer)
                    if self.keyword_params == 0:
                        self.next_state = 'F'
                    else:
                        self.keyword_param_is_required = [False for _ in range(self.keyword_params)]
                        self.next_state = 'E'

            elif self.state == 'E':
                for i in range(self.keyword_params):
                    answer = input(f'   Is keyword parameter #{i + 1} required (y/n)? ').upper()
                    self.keyword_param_is_required[i] = (answer == 'Y')
                self.next_state = 'F'

            elif self.state == 'F':
                answer = input(f'{self.state}: Any VARIABLE KEYWORD PARAMETERS (y/n)? ').upper()
                if answer in self.past_states:
                    self.next_state = answer
                else:
                    self.variable_keyword_params = (answer == 'Y')
                    self.next_state = 'G'

            elif self.state == 'G':
                if self.keyword_params > 0 and not self.variable_positional_params:
                    answer = input(f'{self.state}: Require names when using keyword parameters (y/n)? ').upper()
                    if answer in self.past_states:
                        self.next_state = answer
                    else:
                        self.require_names_for_keyword_params = (answer == 'Y')
                        self.next_state = 'DONE'
                else:
                    self.next_state = 'DONE'

            else:
                print(f'{self.state}: Something went wrong. Not prepared to handle a state of {self.state}.')
                print("Let's start over...")
                self.next_state = 'A'

        # Build up the positional parameters.

        for _ in range(self.required_positional_params):
            self.param_list.append(next(self.param_name_generator))

        for _ in range(self.optional_positional_params):
            self.param_list.append(f'{next(self.param_name_generator)}=default')

        if self.variable_positional_params:
            self.param_list.append('*args')

        # Build up the keyword parameters.

        if self.require_names_for_keyword_params:
            self.param_list.append('*')

        for i in range(self.keyword_params):
            keyword_param = next(self.param_name_generator)
            if not self.keyword_param_is_required[i]:
                keyword_param += '=default'
            self.param_list.append(keyword_param)

        if self.variable_keyword_params:
            self.param_list.append('**kwargs')

        # Build the complete signature.

        signature = 'f('

        for i, param in enumerate(self.param_list):
            signature += ('{}{}'.format(', ' if i > 0 else '', param))

        signature += ')'
        return signature


while True:
    print()
    print()
    signature_creator = FunctionSignatureCreator()
    sig = signature_creator.run()
    print()
    print(f'The function signature is: {sig}')
    print('NOTE: Replace with actual parameter names and default values.')
