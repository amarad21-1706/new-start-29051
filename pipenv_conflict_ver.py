import subprocess
from packaging.version import Version, InvalidVersion

def get_pipenv_graph():
    result = subprocess.run(['pipenv', 'graph'], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')

def filter_problems(graph_output):
    problems = []
    lines = graph_output.split('\n')
    for line in lines:
        if '[required:' in line:
            try:
                parts = line.split('[required:')[1].split(']')[0].strip().split(', installed:')
                required_part = parts[0].strip()
                installed_part = parts[1].strip()

                if 'Any' not in required_part:
                    installed_ver = Version(installed_part)
                    requirement_met = True

                    # Process each requirement separately
                    requirements = required_part.split(', ')
                    for req in requirements:
                        if '<' in req:
                            if not installed_ver < Version(req.replace('<', '').strip()):
                                requirement_met = False
                        elif '<=' in req:
                            if not installed_ver <= Version(req.replace('<=', '').strip()):
                                requirement_met = False
                        elif '>' in req:
                            if not installed_ver > Version(req.replace('>', '').strip()):
                                requirement_met = False
                        elif '>=' in req:
                            if not installed_ver >= Version(req.replace('>=', '').strip()):
                                requirement_met = False
                        elif '==' in req:
                            if not installed_ver == Version(req.replace('==', '').strip()):
                                requirement_met = False

                    # If any of the requirements are not met, add to problems
                    if not requirement_met:
                        problems.append(line.strip())
            except InvalidVersion as iv:
                print(f"Invalid version in line: {line} -> {iv}")
            except Exception as e:
                print(f"Error processing line: {line} -> {e}")

    return problems

graph_output = get_pipenv_graph()
problems = filter_problems(graph_output)
for problem in problems:
    print(problem)
