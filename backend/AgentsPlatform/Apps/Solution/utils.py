from Apps.Agent.models import Agent
import ast
import json


def execute_native(agent, input):
    # Espacio de nombres compartido
    namespace = {}

    # Ejecutar el código del agente en el espacio de nombres
    try:
        exec(agent.pythonCode, namespace)  # El código de 'fib' se define aquí
        print("Namespace después de exec:", namespace)  # Para verificar que la función 'fib' está definida

        # Construir el nombre de la llamada
        name = agent.name + '(' + str(input) + ')'

        # Evaluar la expresión en el mismo espacio de nombres
        answer = eval(name, namespace)
        print('Respuesta:', answer)

    except Exception as e:
        print('Error al ejecutar:', str(e))

    return answer

def execute_no_native(agents, _input):
    i = 0
    memoria = [0] * 10
    output = []
    hand = 0
    _list = json.loads(agents)
    input = json.loads(_input)
    print(_list)
    while i < len(_list):
        if _list[i]['type'] == 'user':
            new_agent = Agent.objects.get(pk=int(_list[i]['id']))
            # print(new_agent.name)
            # print('memoria: ', memoria)
            try:
                if new_agent._type:
                    hand = execute_native(new_agent, memoria)
                else:
                    hand = execute_no_native(new_agent, memoria)
            except:
                return "Error al ejecutar el agente: " + new_agent.name
        
        elif _list[i]['name'] == "inbox":
            if len(input) == 0:
                break
            hand = input[0]
            del input[0]

        elif _list[i]['name'] == "outbox":
            output.append(hand)

        elif _list[i]['name'] == "jump":
            i = _list[i]['target']
            continue

        elif _list[i]['name'] == "jez":
            if hand == 0:
                i = _list[i]['target']
                continue

        elif _list[i]['name'] == "jlz":
            if hand < 0:
                i = _list[i]['target']
                continue

        elif _list[i]['name'] == "jgz":
            if hand > 0:
                i = _list[i]['target']
                continue

        elif _list[i]['name'] == "copyto":
            print('copyto ',_list[i]['target'], ', content:',hand)
            memoria[_list[i]['target']] = hand

        elif _list[i]['name'] == "copyfrom":
            hand = memoria[_list[i]['target']]
            
        i = i + 1
    out = str(output)
    out = out.strip()
    print("-----",out, "-------")
    return out
