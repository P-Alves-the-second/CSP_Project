
from constraint import AllDifferentConstraint

class AllDifferentAttrConstraint(AllDifferentConstraint):
    def __init__(self, attr):
        super().__init__()
        self.attr = attr

    def __call__(self, variables, domains, assignments, forwardcheck=False):
        # Igual ao AllDifferent original, mas com getattr
        seen = set()
        for var in variables:
            if var in assignments:
                val = getattr(assignments[var], self.attr)
                if val in seen:
                    return False
                seen.add(val)
        return True

def not_same_room(aula1,aula2):
    if aula1.sala=="Online" or aula2.sala=="Online":
         return True
    return not (aula1.bloco == aula2.bloco and aula1.sala == aula2.sala)