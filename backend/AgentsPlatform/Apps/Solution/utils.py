from Apps.Agent.models import Agent
import ast


def execute_native(agent, input):
    exec(agent.pythonCode)
    name = agent.name + '(' + str(input) + ')'
    answer = eval(name)
    return answer

def execute_no_native(agents, _input):
    i = 0
    memoria = [0] * 10
    output = []
    hand = 0
    _list = ast.literal_eval(agents)
    input = ast.literal_eval(_input)
    while i < len(_list):
        if type(_list[i]) == type(5):
            new_agent = Agent.objects.get(pk=int(_list[i]))
            try:
                if new_agent._type:
                    hand = execute_native(new_agent, memoria)
                else:
                    hand = execute_no_native(new_agent, memoria)
            except:
                return "Error al ejecutar el agente: " + new_agent.name
            
        elif _list[i] == "inbox":
            if len(input) == 0:
                return output
            hand = input[0]
            del input[0]

        elif _list[i] == "outbox":
            output.append(hand)

        elif _list[i][0] == "jump":
            i = _list[i][1]
            continue

        elif _list[i][0] == "jez":
            if hand == 0:
                i = _list[i][1]
                continue

        elif _list[i][0] == "jlz":
            if hand > 0:
                i = _list[i][1]
                continue

        elif _list[i][0] == "jgz":
            if hand > 0:
                i = _list[i][1]
                continue

        elif _list[i][0] == "copyTo":
            memoria[_list[i][1]] = hand

        elif _list[i][0] == "copyFrom":
            hand = memoria[_list[i][1]]
            
        i = i + 1
    return str(output)
