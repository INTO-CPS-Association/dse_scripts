import re

def BoundOrganisms(organisms: list, constraints: dict) -> list:

    for o in organisms:
        for k in o:
            if k not in constraints.keys():
                continue

            if constraints[k][0] > o[k]:
                o[k] = constraints[k][0]
            elif constraints[k][1] < o[k]:
                o[k] = constraints[k][1]

    return organisms

def CheckOrganismConstraints(organism, constraints):
    for constraint in constraints:
        if not eval(ReplaceWithQualifiedNames(organism, constraint)):
            return False

    return True

def ReplaceWithQualifiedNames(organism, constraint):
    result = constraint

    for name in organism.keys():
        escapedName = re.escape(name) # we need to escape for regex searching to avoid any issues
        reString = fr"(\b({escapedName})\b)|((?!\w)({escapedName})(?!\w))"
        # reString = f"\\b{name}\\b"
        result = re.sub(reString, f"organism['{name}']", result)

    return result
