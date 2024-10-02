import subprocess

def get_pipenv_graph():
    result = subprocess.run(['pipenv', 'graph'], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')

def filter_problems(graph_output):
    # This is a placeholder: you would need to define what constitutes a "problem"
    problems = [line for line in graph_output.split('\n') if 'conflict' in line.lower()]
    return problems

graph_output = get_pipenv_graph()
problems = filter_problems(graph_output)
for problem in problems:
    print(problem)
